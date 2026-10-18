from copy import deepcopy
from jsonschema.validators import validator_for
from app.tools.catalog import HIDDEN_PARAMETERS
from app.tools.types import ToolOutcome


def validate_arguments(definition, arguments):
    if not isinstance(arguments, dict) or HIDDEN_PARAMETERS.intersection(arguments):
        return ToolOutcome({'error': {'code': 'invalid_arguments',
            'message': '参数必须为业务字段对象，不能填写内部身份或确认字段。'}}, 'error', 0)
    schema = deepcopy(definition.input_schema)
    # A permissive external object must never accept extra model-injected authority.
    errors = list(validator_for(schema)(schema).iter_errors(arguments))
    if errors:
        paths = [('.'.join(map(str, error.absolute_path)) or '$') for error in errors[:5]]
        return ToolOutcome({'error': {'code': 'invalid_arguments',
            'message': '工具参数不符合定义，请核对类型、必填项及取值范围。', 'fields': paths}}, 'error', 0)
    return deepcopy(arguments)
