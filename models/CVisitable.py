class AbstractVisitable:
    def accept(self, abstractVisitor):
        pass


class AbstractVisitor:
    def visit(self, visitable):
        pass
