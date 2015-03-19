from .EnvVarCondition import *
from .EnvVariable import *
from ...XCConfig.xcconfig import *
from ....Helpers import logging_helper

class Environment(object):
    
    def __init__(self):
        self.settings = {};
        # load default environment types
        
        # setting up default environment
        self.applyConfig(xcconfig(None));
    
    def addOptions(self, options_array):
        for item in options_array:
            if item['Name'] in self.settings.keys():
                print 'over-write key %s' % item['Name'];
                #print item;
            else:
                self.settings[item['Name']] = EnvVariable(item);
    
    def applyConfig(self, config_obj):
        for line in config_obj.lines:
            if line.type == 'KV':
                self.setValueForKey(line.key(), line.value(None), line.conditions());
            if line.type == 'COMMENT':
                # ignore this type of line
                continue;
            if line.type == 'INCLUDE':
                base_path = os.path.dirname(config_obj.path);
                path = line.includePath(base_path);
                self.applyConfig(xcconfig(path));
    
    def isEnvironmentVariable(self, key_string):
        is_envar = False;
        find_sub = key_string.find('$');
        if find_sub != -1:
            offset = find_sub + 1;
            next_char = key_string[offset];
            if next_char == '(' or next_char == '{':
                is_envar = True;
        return is_envar;
    
    def parseKey(self, key_string):
        key = '';
        value = '';
        string_length = len(key_string);
        offset = 0;
        key_length = 0;
        find_sub = key_string.find('$');
        if find_sub != -1:
            start = find_sub;
            end = 0;
            offset = find_sub + 1;
            next_char = key_string[offset];
            if next_char == '(' or next_char == '{':
                offset += 1;
                while offset < string_length:
                    if key_string[offset] == '$':
                        print 'found subkey';
                        subkey = key_string[offset:];
                        sub_value = self.parseKey(subkey);
                        if sub_value[0] == False:
                            logging_helper.getLogger().error('[Environment]: Error in parsing key "%s"' % key_string);
                        key += sub_value[1];
                        offset += sub_value[2];
                    elif key_string[offset] == ')' or key_string[offset] == '}':
                        end = offset;
                        break;
                    else:
                        key += key_string[offset];
                    offset += 1;
                value = self.valueForKey(key);
                key_length = end - start;
        return (key_length != 0, value, key_length);
    
    def setValueForKey(self, key, value, condition_dict):
        if key not in self.settings.keys():
            option_dict = {};
            option_dict['Name'] = key;
            if len(condition_dict.keys()) == 0:
                option_dict['DefaultValue'] = value;
            else:
                option_dict['DefaultValue'] = '';
            self.settings[key] = EnvVariable(option_dict);
        if key in self.settings.keys():
            result = self.settings[key];
            if result != None:
                result.addConditionalValue(EnvVarCondition(condition_dict, value));
        
    
    def valueForKey(self, key):
        value = None;
        if key in self.settings.keys():
            result = self.settings[key];
            if result != None:
                value = result.value(self);
        return value;