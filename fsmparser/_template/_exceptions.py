class FSMError(Exception):
    ...


class TemplateError(FSMError):
    ...


class TemplateNotFound(TemplateError):
    ...
