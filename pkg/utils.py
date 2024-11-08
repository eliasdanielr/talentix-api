def remove_bearer_prefix(token: str) -> str:
    return token.removeprefix("Bearer")