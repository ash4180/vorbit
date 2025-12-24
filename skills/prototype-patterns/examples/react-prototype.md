# React Prototype Example

## Scenario

Prototyping a user profile page based on PRD.

## Generated Files

### `src/components/Profile/ProfilePrototype.jsx`

```jsx
import { useState } from 'react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { Avatar } from '../ui/Avatar';

// Mock data - matches GET /api/users/:id response
const MOCK_USER = {
  id: 1,
  name: "Jane Doe",
  email: "jane@example.com",
  avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=jane",
  role: "admin",
  joinedAt: "2024-01-15T00:00:00Z",
  stats: {
    posts: 42,
    followers: 128,
    following: 64
  }
};

export function ProfilePrototype() {
  const [user, setUser] = useState(MOCK_USER);
  const [isEditing, setIsEditing] = useState(false);

  const handleSave = () => {
    // TODO: Replace with API call
    console.log('Saving:', user);
    setIsEditing(false);
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <Card>
        <div className="flex items-center gap-4 mb-6">
          <Avatar src={user.avatar} size="lg" />
          <div>
            <h1 className="text-2xl font-bold">{user.name}</h1>
            <p className="text-gray-500">{user.email}</p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-6 text-center">
          <div>
            <div className="text-2xl font-bold">{user.stats.posts}</div>
            <div className="text-sm text-gray-500">Posts</div>
          </div>
          <div>
            <div className="text-2xl font-bold">{user.stats.followers}</div>
            <div className="text-sm text-gray-500">Followers</div>
          </div>
          <div>
            <div className="text-2xl font-bold">{user.stats.following}</div>
            <div className="text-sm text-gray-500">Following</div>
          </div>
        </div>

        {isEditing ? (
          <div className="space-y-4">
            <input
              type="text"
              value={user.name}
              onChange={(e) => setUser({ ...user, name: e.target.value })}
              className="w-full p-2 border rounded"
            />
            <div className="flex gap-2">
              <Button onClick={handleSave}>Save</Button>
              <Button variant="secondary" onClick={() => setIsEditing(false)}>
                Cancel
              </Button>
            </div>
          </div>
        ) : (
          <Button onClick={() => setIsEditing(true)}>Edit Profile</Button>
        )}
      </Card>
    </div>
  );
}
```

## Key Points

1. **Uses existing components** - Button, Card, Avatar from `ui/`
2. **Inline mock data** - MOCK_USER at top, matches API shape
3. **Minimal state** - Just user and isEditing
4. **No tests** - Prototype only
5. **TODO marker** - Shows where real API goes

## How to Swap to Real API

```diff
- const MOCK_USER = { ... };
- const [user, setUser] = useState(MOCK_USER);
+ const { data: user, mutate } = useSWR('/api/users/me');

  const handleSave = () => {
-   console.log('Saving:', user);
+   await fetch('/api/users/me', {
+     method: 'PATCH',
+     body: JSON.stringify(user)
+   });
+   mutate();
    setIsEditing(false);
  };
```
