import javalang


def is_java_function(code_snippet: str) -> bool:
    """Return True when the snippet parses as a single Java method or constructor."""
    if not code_snippet:
        return False

    snippet = code_snippet.strip()
    if not snippet:
        return False

    wrappers = (
        "abstract class Dummy {\n%s\n}",
        "interface Dummy {\n%s\n}",
    )

    for template in wrappers:
        wrapped = template % snippet
        try:
            tree = javalang.parse.parse(wrapped)
        except (javalang.parser.JavaSyntaxError, javalang.tokenizer.LexerError, TypeError):
            continue

        if not tree.types:
            continue

        type_decl = tree.types[0]
        members = getattr(type_decl, "body", [])
        method_members = [
            member
            for member in members
            if isinstance(member, (javalang.tree.MethodDeclaration, javalang.tree.ConstructorDeclaration))
        ]

        if len(method_members) != 1:
            continue

        if len(members) == 1:
            return True

    return False
