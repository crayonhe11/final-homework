"""语法白名单。学生代码仅在可终止的浏览器Worker中执行，不在服务器执行。"""
import ast
import json


SAFE_CALLS={'abs','all','any','bool','dict','enumerate','float','int','len','list','max','min','print','range','reversed','round','sorted','str','sum','tuple','zip'}
SAFE_METHODS={'append','extend','count','index','reverse','sort','pop','insert','remove','clear','copy','get','keys','values','items','lower','upper','strip','split','join','startswith','endswith','replace'}
ALLOWED_NODES={
 'Module','FunctionDef','arguments','arg','Return','Assign','AugAssign','If','For','While','Break','Continue','Pass','Expr',
 'Name','Load','Store','Constant','List','Tuple','Dict','Set','Subscript','Slice','Call','keyword','Attribute',
 'BinOp','UnaryOp','BoolOp','Compare','IfExp','JoinedStr','FormattedValue','ListComp','DictComp','SetComp','comprehension',
 'Add','Sub','Mult','Div','FloorDiv','Mod','Pow','UAdd','USub','Not','And','Or','Eq','NotEq','Lt','LtE','Gt','GtE','In','NotIn','Is','IsNot'}


def validate_source(source):
    if not isinstance(source,str) or len(source)>20000: raise ValueError('代码最多20,000字符')
    tree=ast.parse(source,filename='student.py')
    nodes=list(ast.walk(tree))
    if len(nodes)>3000: raise ValueError('代码结构过于复杂')
    functions={n.name for n in nodes if isinstance(n,ast.FunctionDef)}
    for node in nodes:
        if type(node).__name__ not in ALLOWED_NODES:
            raise ValueError(f'第{getattr(node,"lineno",1)}行：本练习环境不支持 {type(node).__name__}；仅支持基础计算、条件、循环和函数。')
        if isinstance(node,(ast.Name,ast.arg,ast.FunctionDef)):
            name=getattr(node,'id',getattr(node,'arg',getattr(node,'name','')))
            if name.startswith('_'): raise ValueError('不允许以下划线开头的内部名称')
        if isinstance(node,ast.FunctionDef) and (node.decorator_list or node.returns or getattr(node,"type_params",[])):
            raise ValueError('本环境不支持装饰器、返回注解或泛型')
        if isinstance(node,ast.arg) and node.annotation: raise ValueError('本环境请先省略类型注解')
        if isinstance(node,ast.Attribute) and node.attr not in SAFE_METHODS: raise ValueError('不支持该属性访问：'+node.attr)
        if isinstance(node,ast.Call):
            valid=isinstance(node.func,ast.Name) and node.func.id in SAFE_CALLS|functions
            valid=valid or isinstance(node.func,ast.Attribute) and node.func.attr in SAFE_METHODS
            if not valid: raise ValueError('不支持该函数调用；不能导入模块、读写文件或访问网络')
        if isinstance(node,ast.Constant) and isinstance(node.value,(str,bytes)) and len(node.value)>10000:
            raise ValueError('文本常量过长')
    return tree
