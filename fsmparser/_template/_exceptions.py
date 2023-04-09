class FSMError(Exception):
    ...


class TemplateError(FSMError):
    ...


class ParseError(TemplateError):
    ...


class TemplateNotFound(TemplateError):
    ...
