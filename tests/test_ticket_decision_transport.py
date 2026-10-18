from langchain_openai import ChatOpenAI


def test_native_ticket_transport_does_not_force_parameters_into_json_body():
    from app.workflow.agent import decision_transport_model
    model = ChatOpenAI(api_key='offline-test', extra_body={'max_tokens': 2048})
    write = decision_transport_model(model, ticket_requested=True)
    read = decision_transport_model(model, ticket_requested=False)
    assert write.extra_body == {'max_tokens': 2048}
    assert read.extra_body['response_format'] == {'type': 'json_object'}
    assert model.extra_body == {'max_tokens': 2048}


def test_dynamic_read_catalog_uses_native_calls_without_json_body_override():
    from app.workflow.agent import decision_transport_model
    model = ChatOpenAI(api_key='offline-test', extra_body={'max_tokens': 2048})
    native = decision_transport_model(model, native_catalog=True)
    assert native.extra_body == {'max_tokens': 2048}
