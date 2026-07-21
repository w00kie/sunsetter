from urllib.parse import parse_qs, urlparse

from workers import Response, WorkerEntrypoint

from solar import matching_days


def _number(value: object, name: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be a number") from error


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        url = urlparse(request.url)

        if url.path == "/api/matches":
            if request.method not in ("GET", "POST"):
                return Response.json({"error": "Method not allowed"}, status=405)
            try:
                data = await request.json() if request.method == "POST" else {
                    key: values[0] for key, values in parse_qs(url.query).items()
                }
                result = matching_days(_number(data.get("lat"), "lat"), _number(data.get("az"), "az"))
                return Response.json(result, headers={"Cache-Control": "public, max-age=86400"})
            except ValueError as error:
                return Response.json({"error": str(error)}, status=400)

        return await self.env.ASSETS.fetch(request)
