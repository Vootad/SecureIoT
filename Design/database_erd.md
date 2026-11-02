
erDiagram

    USERS {
        int id PK
        string username UK
        string password_hash
        string role
        int is_active
        datetime created_at
    }

    LOCKS {
        int id PK
        string lock_id UK
        string password_hash
        int is_active
        datetime created_at
    }

    USER_LOCK_PERMISSIONS {
        int id PK
        int user_id FK
        int lock_id FK
        datetime created_at
    }

    AUDIT_LOGS {
        int id PK
        datetime timestamp
        string username
        string ip_address
        string event_type
        string result
        string reason
        string previous_hash
        string current_hash
    }

    USED_NONCE {
        int id PK
        string nonce UK
        datetime created_at
    }

    UNLOCK_ATTEMPTS {
        int id PK
        string username
        string lock_id
        int failed_attempts
        datetime blocked_until
    }

    LOGIN_ATTEMPTS {
        int id PK
        string username
        string ip
        int failed_attempts
        datetime blocked_until
    }

    USERS ||--o{ USER_LOCK_PERMISSIONS : has
    LOCKS ||--o{ USER_LOCK_PERMISSIONS : assigned_to
