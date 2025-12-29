import ast
import re

def to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def to_camel_case(name):
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

class ForLoopToListComprehensionTransformer(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        new_body = []
        i = 0
        while i < len(node.body):
            stmt = node.body[i]
            transformed = False
            if (isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.List) and not stmt.value.elts and
                i + 1 < len(node.body) and isinstance(node.body[i+1], ast.For)):
                
                for_loop = node.body[i+1]
                if not for_loop.orelse:
                    if_stmt = None
                    append_stmt = None

                    if len(for_loop.body) == 1:
                        if isinstance(for_loop.body[0], ast.If) and len(for_loop.body[0].body) == 1:
                            if_stmt = for_loop.body[0]
                            append_stmt = if_stmt.body[0]
                        elif isinstance(for_loop.body[0], ast.Expr):
                            append_stmt = for_loop.body[0]

                    if (append_stmt and isinstance(append_stmt.value, ast.Call) and
                        isinstance(append_stmt.value.func, ast.Attribute) and
                        append_stmt.value.func.attr == 'append' and
                        isinstance(append_stmt.value.func.value, ast.Name) and
                        append_stmt.value.func.value.id == stmt.targets[0].id):

                        list_comp = ast.Assign(
                            targets=[stmt.targets[0]],
                            value=ast.ListComp(
                                elt=append_stmt.value.args[0],
                                generators=[ast.comprehension(
                                    target=for_loop.target,
                                    iter=for_loop.iter,
                                    ifs=[if_stmt.test] if if_stmt else [],
                                    is_async=0
                                )]
                            )
                        )
                        new_body.append(ast.copy_location(list_comp, stmt))
                        i += 2
                        transformed = True
            
            if not transformed:
                new_body.append(stmt)
                i += 1
        node.body = new_body
        return node

class CommentGenerator(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        # Generate a simple docstring
        docstring = f'This function, `{node.name}`, takes the following arguments: {", ".join([arg.arg for arg in node.args.args])} and returns a result.'

        # Create a docstring node
        docstring_node = ast.Expr(value=ast.Constant(value=docstring))

        # Insert the docstring as the first statement in the function body
        node.body.insert(0, docstring_node)

        return node

class NamingConventionTransformer(ast.NodeTransformer):
    def __init__(self, convention):
        self.convention = convention
        self.rename_map = {}

    def visit_FunctionDef(self, node):
        # Rename function name
        if self.convention == 'snake_case':
            node.name = to_snake_case(node.name)
        elif self.convention == 'camelCase':
            node.name = to_camel_case(node.name)

        # Process function body
        self.rename_map = {} # Reset for new scope
        self.generic_visit(node)
        return node

    def visit_arg(self, node):
        original_name = node.arg
        if self.convention == 'snake_case':
            new_name = to_snake_case(original_name)
        elif self.convention == 'camelCase':
            new_name = to_camel_case(original_name)
        else:
            new_name = original_name

        if new_name != original_name:
            self.rename_map[original_name] = new_name
        node.arg = new_name
        return node

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            original_name = node.id
            if self.convention == 'snake_case':
                new_name = to_snake_case(original_name)
            elif self.convention == 'camelCase':
                new_name = to_camel_case(original_name)
            else:
                new_name = original_name

            if new_name != original_name:
                self.rename_map[original_name] = new_name
            node.id = new_name
        elif isinstance(node.ctx, ast.Load) and node.id in self.rename_map:
            node.id = self.rename_map[node.id]
        return node

def humanize_code(code, options):
    """
    Parses the given Python code, applies humanization transformations,
    and returns the transformed code.
    """
    try:
        tree = ast.parse(code)
        
        # Add comments to the code
        if options.get('add_comments'):
            comment_generator = CommentGenerator()
            tree = comment_generator.visit(tree)

        # Change naming convention
        naming_convention = options.get('naming_convention')
        if naming_convention:
            transformer = NamingConventionTransformer(naming_convention)
            tree = transformer.visit(tree)

        # Transform for loops to list comprehensions
        if options.get('convert_loops'):
            tree = ForLoopToListComprehensionTransformer().visit(tree)
        
        transformed_code = ast.unparse(tree)
        return transformed_code
    except SyntaxError as e:
        return f"Error: Invalid Python code - {e}"

if __name__ == '__main__':
    # Example usage for testing
    ai_code = """
def my_function(a, b):
    return a + b
"""
    humanized_code = humanize_code(ai_code, {})
    print(humanized_code)
