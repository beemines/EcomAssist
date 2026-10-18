from langchain_openai import ChatOpenAI


def test_native_ticket_transport_does_not_force_parameters_into_json_body():
    from app.workflow.agent import decision_transport_model
    model = ChatOpenAI(api_key='offline-test', extra_body={'max_tokens': 2048})
    write = decision_transport_model(model, ticket_requested=True)
    read = decision_transport_model(model, ticket_requested=False)
    assert write.extra_body == {'max_tokens': 2048}
    assert read.extra_body['response_format'] == {'type': 'json_object'}
    assert model.extra_body == {'max_tokens': 2048}
