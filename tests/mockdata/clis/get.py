mock_get_by_identity ={
    "traits": [
        {"id": 1, "trait_key": "email", "trait_value": "example@example.com"},
        {"id": 2, "trait_key": "organisations", "trait_value": '"1"'},
        {"id": 3, "trait_key": "logins", "trait_value": 2},
        {"id": 4, "trait_key": "preferred_language", "trait_value": "Python"},
        {"id": 5, "trait_key": "first_feature", "trait_value": "true"},
    ],
    "flags": [
        {
            "id": 1,
            "feature": {
                "id": 1,
                "name": "flag_name",
                "created_date": "2024-05-31T12:33:06.147764Z",
                "description": "flag_name description",
                "initial_value": "https://example.com",
                "default_enabled": True,
                "type": "STANDARD",
            },
            "feature_state_value": "https://example.com",
            "environment": 1,
            "identity": None,
            "feature_segment": None,
            "enabled": True,
        }
    ],
}
