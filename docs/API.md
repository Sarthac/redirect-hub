# API Reference

The API allows you to interact with your shortened URLs programmatically. To use the API, you need to include your API key in the `X-API-Key` header of your requests.

## Authentication

Authentication is done by passing an API key in the `X-API-Key` header.

```
X-API-Key: YOUR_API_KEY
```

## Endpoints

### Test Server

Check if the server is operational.

- **Method:** `GET`
- **URL:** `/api/test`
- **Authentication:** Not required.

**Response (200 OK)**

```json
{
  "data": "Server is operational."
}
```

---

### List All Routes

Retrieve a paginated list of all your routes.

- **Method:** `GET`
- **URL:** `/api/routes`
- **Authentication:** Required.

**Query Parameters**

- `limit` (optional): Number of results per page. Default: `20`.
- `page` (optional): Page number. Default: `1`.
- `sortBy` (optional): Sort by `created_at`, `route`, `url`, or `updated_at`. Default: `created_at`.
- `sortOrder` (optional): Sort order `asc` or `desc`. Default: `asc`.

**Response (200 OK)**

```json
{
  "data": [
    {
      "route": "example",
      "url": "http://example.com",
      "created_at": "2023-10-27 10:00:00",
      "update_at": "2023-10-27 10:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "totalPages": 1
}
```

---

### Create a New Route

Create a new shortened URL.

- **Method:** `POST`
- **URL:** `/api/routes`
- **Authentication:** Required.

**Request Body**

```json
{
  "url": "http://example.com",
  "route": "custom-route" // optional
}
```

**Response (201 Created)**

```json
{
  "data": {
    "route": "custom-route",
    "url": "http://example.com"
  }
}
```

**Error Response (400 Bad Request)**

If the route already exists:

```json
{
  "error": "Route already exists, provide unique route"
}
```

---

### Get a Specific Route

Retrieve information about a specific route.

- **Method:** `GET`
- **URL:** `/api/routes/<route>`
- **Authentication:** Required.

**URL Parameters**

- `route`: The route to retrieve.

**Response (200 OK)**

```json
{
  "data": {
    "route": "example",
    "url": "http://example.com",
    "created_at": "2023-10-27 10:00:00",
    "update_at": "2023-10-27 10:00:00"
  }
}
```

**Error Response (404 Not Found)**

```json
{
  "error": "Route does not exist."
}
```

---

### Update a Route

Update the URL or the route of a shortened URL.

- **Method:** `PATCH`
- **URL:** `/api/routes/<route>`
- **Authentication:** Required.

**URL Parameters**

- `route`: The route to update.

**Request Body**

You can provide a new `url`, a new `route`, or both.

```json
{
  "url": "http://new-example.com",
  "route": "new-custom-route"
}
```

**Response (200 OK)**

```json
{
  "message": "Route updated successfully."
}
```

**Error Response (400 Bad Request)**

If the new route already exists:

```json
{
  "error": "New route already exists"
}
```

---

### Delete a Route

Delete a shortened URL.

- **Method:** `DELETE`
- **URL:** `/api/routes/<route>`
- **Authentication:** Required.

**URL Parameters**

- `route`: The route to delete.

**Response (204 No Content)**

An empty response with a `204` status code indicates successful deletion.
