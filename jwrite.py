class JavaClass:

    def __init__(self, class_name):
        self.class_name = class_name
        self.package = None
        self.imports = []
        self.vars = []
    
    def write_all(self, outfile=None):
        lines = []
        if self.package is not None:
            lines.append('package {};'.format(self.package))
            lines.append('')
        if self.imports:
            lines.append(self.write_imports())
            lines.append('')
        lines.append('public class {} {{'.format(self.class_name))
        lines.append('')
        for name, type, init_val in self.vars:
            lines.append('    private {} {};'.format(type, name))
        lines.append('')
        if [i for i in self.vars if i[2]]:
            lines.append(self.write_constructor())
            lines.append('')
        for name, type, init_val in self.vars:
            lines.append(self.write_getter(name, type))
            lines.append(self.write_setter(name, type))
        lines.append('}')
        to_write = '\n'.join(lines)
        if outfile:
            with open(outfile, 'w') as f:
                f.write(to_write)
        else:
            print(to_write)
    
    def add_var(self, name, type, init_val=None):
        self.vars.append([name, type, init_val])
    
    def write_imports(self):
        lines = ['import {};'.format(i) for i in self.imports]
        return '\n'.join(lines)
    
    def write_constructor(self):
        lines = ['    public {name} () {{'.format(name=self.class_name)]
        for name, type, init_val in self.vars:
            if init_val is not None:
                line = '        {var} = {val};'.format(var=name, val=init_val)
                lines.append(line)
        lines.append('    }')
        return '\n'.join(lines)

    def write_getter(self, varname, vartype): 
        method_name = 'get' + varname[0].upper() + varname[1:]
        func = '    public {type} {name}() {{\n        return {var};\n    }}\n'
        return func.format(type=vartype, name=method_name, var=varname)
       
    def write_setter(self, varname, vartype):
        method_name = 'set' + varname[0].upper() + varname[1:]
        func = '    public void {name}({type} {var}) {{\n        this.{var} = {var};\n    }}\n'
        return func.format(type=vartype, name=method_name, var=varname)
        

def test():
    jc = JavaClass('TestClass')
    jc.package = 'test_package'
    jc.add_var('color', 'String', '"red"')
    jc.add_var('speed', 'int', '55')
    jc.imports = ['java.util.testImport', 'java.util.anotherTest']
    jc.write_all('/home/bunburya/test.java')
