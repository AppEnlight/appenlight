# -*- coding: utf-8 -*-

# Copyright (C) 2010-2016  RhodeCode GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License, version 3
# (only), as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This program is dual-licensed. If you wish to learn more about the
# App Enlight Enterprise Edition, including its added features, Support
# services, and proprietary license terms, please see
# https://rhodecode.com/licenses/

import logging
import operator

log = logging.getLogger(__name__)


class RuleException(Exception):
    pass


class KeyNotFoundException(RuleException):
    pass


class UnknownTypeException(RuleException):
    pass


class BadConfigException(RuleException):
    pass


class InvalidValueException(RuleException):
    pass


class RuleBase(object):
    @classmethod
    def default_dict_struct_getter(cls, struct, field_name):
        """
        returns a key from dictionary based on field_name, if the name contains
        `:` then it means additional nesting levels should be checked for the
        key so `a:b:c` means return struct['a']['b']['c']

        :param struct:
        :param field_name:
        :return:
        """
        parts = field_name.split(':') if field_name else []
        found = struct
        while parts:
            current_key = parts.pop(0)
            found = found.get(current_key)
            if not found and parts:
                raise KeyNotFoundException('Key not found in structure')
        return found

    @classmethod
    def default_obj_struct_getter(cls, struct, field_name):
        """
        returns a key from instance based on field_name, if the name contains
        `:` then it means additional nesting levels should be checked for the
        key so `a:b:c` means return struct.a.b.c

        :param struct:
        :param field_name:
        :return:
        """
        parts = field_name.split(':')
        found = struct
        while parts:
            current_key = parts.pop(0)
            found = getattr(found, current_key, None)
            if not found and parts:
                raise KeyNotFoundException('Key not found in structure')
        return found

    def normalized_type(self, field, value):
        """
        Converts text values from self.conf_value based on type_matrix below
        check_matrix defines what kind of checks we can perform on a field
        value based on field name
        """
        f_type = self.type_matrix.get(field)
        if f_type:
            cast_to = f_type['type']
        else:
            raise UnknownTypeException('Unknown type')

        if value is None:
            return None

        try:
            if cast_to == 'int':
                return int(value)
            elif cast_to == 'float':
                return float(value)
            elif cast_to == 'unicode':
                return str(value)
        except ValueError as exc:
            raise InvalidValueException(exc)


class Rule(RuleBase):
    def __init__(self, config, type_matrix,
                 struct_getter=RuleBase.default_dict_struct_getter,
                 config_manipulator=None):
        """

        :param config: dict - contains rule configuration
                              example::
                                    {
                                        "field": "__OR__",
                                        "rules": [
                                            {
                                                "field": "__AND__",
                                                "rules": [
                                                    {
                                                        "op": "ge",
                                                        "field": "occurences",
                                                        "value": "10"
                                                    },
                                                    {
                                                        "op": "ge",
                                                        "field": "priority",
                                                        "value": "4"
                                                    }
                                                ]
                                            },
                                            {
                                                "op": "eq",
                                                "field": "http_status",
                                                "value": "500"
                                            }
                                        ]
                                    }
        :param type_matrix: dict - contains map of type casts
                                   example::
                                        {
                                        'http_status': 'int',
                                        'priority': 'unicode',
                                        }
        :param struct_getter: callable - used to grab the value of field from
                                         the structure passed to match() based
                                         on key, default

        """
        self.type_matrix = type_matrix
        self.config = config
        self.struct_getter = struct_getter
        self.config_manipulator = config_manipulator
        if config_manipulator:
            config_manipulator(self)

    def subrule_check(self, rule_config, struct):
        rule = Rule(rule_config, self.type_matrix,
                    config_manipulator=self.config_manipulator)
        return rule.match(struct)

    def match(self, struct):
        """
        Check if rule matched for this specific report
        First tries report value, then tests tags in not found, then finally
        report group
        """
        field_name = self.config.get('field')
        test_value = self.config.get('value')

        if not field_name:
            return False

        if field_name == '__AND__':
            rule = AND(self.config['rules'], self.type_matrix,
                       config_manipulator=self.config_manipulator)
            return rule.match(struct)
        elif field_name == '__OR__':
            rule = OR(self.config['rules'], self.type_matrix,
                      config_manipulator=self.config_manipulator)
            return rule.match(struct)

        if test_value is None:
            return False

        try:
            struct_value = self.normalized_type(field_name,
                                                self.struct_getter(struct,
                                                                   field_name))
        except (UnknownTypeException, InvalidValueException) as exc:
            log.error(str(exc))
            return False

        try:
            test_value = self.normalized_type(field_name, test_value)
        except (UnknownTypeException, InvalidValueException) as exc:
            log.error(str(exc))
            return False

        if self.config['op'] not in ('startswith', 'endswith', 'contains'):
            try:
                return getattr(operator,
                               self.config['op'])(struct_value, test_value)
            except TypeError:
                return False
        elif self.config['op'] == 'startswith':
            return struct_value.startswith(test_value)
        elif self.config['op'] == 'endswith':
            return struct_value.endswith(test_value)
        elif self.config['op'] == 'contains':
            return test_value in struct_value
        raise BadConfigException('Invalid configuration, '
                                 'unknown operator: {}'.format(self.config))

    def __repr__(self):
        return '<Rule {} {}>'.format(self.config.get('field'),
                                     self.config.get('value'))


class AND(Rule):
    def __init__(self, rules, *args, **kwargs):
        super(AND, self).__init__({}, *args, **kwargs)
        self.rules = rules

    def match(self, struct):
        return all([self.subrule_check(r_conf, struct) for r_conf
                    in self.rules])


class OR(Rule):
    def __init__(self, rules, *args, **kwargs):
        super(OR, self).__init__({}, *args, **kwargs)
        self.rules = rules

    def match(self, struct):
        return any([self.subrule_check(r_conf, struct) for r_conf
                    in self.rules])


class RuleService(object):
    @staticmethod
    def rule_from_config(config, field_mappings, labels_dict,
                         manipulator_func=None):
        """
        Returns modified rule with manipulator function
        By default manipulator function replaces field id from labels_dict
        with current field id proper for the rule from fields_mappings

        because label X_X id might be pointing different value on next request
        when new term is returned from elasticsearch - this ensures things
        are kept 1:1 all the time
        """
        rev_map = {}
        for k, v in labels_dict.items():
            rev_map[(v['agg'], v['key'],)] = k

        if manipulator_func is None:
            def label_rewriter_func(rule):
                field = rule.config.get('field')
                if not field or rule.config['field'] in ['__OR__', '__AND__']:
                    return

                to_map = field_mappings.get(rule.config['field'])

                # we need to replace series field with _AE_NOT_FOUND_ to not match
                # accidently some other field which happens to have the series that
                # was used when the alert was created
                if to_map:
                    to_replace = rev_map.get((to_map['agg'], to_map['key'],),
                                             '_AE_NOT_FOUND_')
                else:
                    to_replace = '_AE_NOT_FOUND_'

                rule.config['field'] = to_replace
                rule.type_matrix[to_replace] = {"type": 'float'}

            manipulator_func = label_rewriter_func

        return Rule(config, {}, config_manipulator=manipulator_func)
