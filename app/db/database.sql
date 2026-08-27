CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,

    login VARCHAR(64) NOT NULL UNIQUE,
    password_hash TEXT,

    nickname VARCHAR(32) NOT NULL,
    color VARCHAR(7) NOT NULL,

    wca_id VARCHAR(20) UNIQUE,

    nickname_changed_at TIMESTAMPTZ,
    color_changed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE sessions (
    id UUID PRIMARY KEY,

    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,

    nickname VARCHAR(32),
    color VARCHAR(7),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,

    CHECK (
        user_id IS NOT NULL
        OR (nickname IS NOT NULL AND color IS NOT NULL)
    )
);


CREATE TABLE rooms (
    id BIGSERIAL PRIMARY KEY,

    code VARCHAR(8) NOT NULL UNIQUE,

    owner_member_id BIGINT,

    event VARCHAR(16) NOT NULL,

    current_round_id BIGINT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE room_members (
    id BIGSERIAL PRIMARY KEY,

    room_id BIGINT NOT NULL
        REFERENCES rooms(id) ON DELETE CASCADE,

    session_id UUID NOT NULL
        REFERENCES sessions(id) ON DELETE CASCADE,

    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(room_id, session_id)
);


ALTER TABLE rooms
ADD CONSTRAINT fk_room_owner
FOREIGN KEY (owner_member_id)
REFERENCES room_members(id)
ON DELETE SET NULL;


CREATE TABLE rounds (
    id BIGSERIAL PRIMARY KEY,

    room_id BIGINT NOT NULL
        REFERENCES rooms(id) ON DELETE CASCADE,

    number INTEGER NOT NULL,

    scramble TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(room_id, number)
);


ALTER TABLE rooms
ADD CONSTRAINT fk_current_round
FOREIGN KEY (current_round_id)
REFERENCES rounds(id)
ON DELETE SET NULL;


CREATE TABLE round_members (
    round_id BIGINT NOT NULL
        REFERENCES rounds(id) ON DELETE CASCADE,

    member_id BIGINT NOT NULL
        REFERENCES room_members(id) ON DELETE CASCADE,

    PRIMARY KEY(round_id, member_id)
);


CREATE TABLE round_solves (
    id BIGSERIAL PRIMARY KEY,

    round_id BIGINT NOT NULL
        REFERENCES rounds(id) ON DELETE CASCADE,

    member_id BIGINT NOT NULL
        REFERENCES room_members(id) ON DELETE CASCADE,

    time NUMERIC(10,3) NOT NULL,

    penalty VARCHAR(8) NOT NULL DEFAULT 'NONE',

    UNIQUE(round_id, member_id),

    CHECK (penalty IN ('NONE', 'PLUS_TWO', 'DNF'))
);


CREATE TABLE user_solves (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL
        REFERENCES users(id) ON DELETE CASCADE,

    event VARCHAR(16) NOT NULL,

    scramble TEXT NOT NULL,

    time NUMERIC(10,3) NOT NULL,

    penalty VARCHAR(8) NOT NULL DEFAULT 'NONE',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CHECK (penalty IN ('NONE', 'PLUS_TWO', 'DNF'))
);


CREATE INDEX idx_room_members_room
ON room_members(room_id);

CREATE INDEX idx_rounds_room
ON rounds(room_id);

CREATE INDEX idx_round_members_round
ON round_members(round_id);

CREATE INDEX idx_round_solves_round
ON round_solves(round_id);

CREATE INDEX idx_user_solves_user
ON user_solves(user_id);

CREATE INDEX idx_user_solves_user_event
ON user_solves(user_id, event);