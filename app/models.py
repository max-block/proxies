from __future__ import annotations

from datetime import datetime
from enum import Enum, unique

from mb_std import utc_delta, utc_now
from mb_std.mongo import MongoModel, ObjectIdStr
from pydantic import BaseModel, Field, HttpUrl


@unique
class ProxyType(str, Enum):
    SOCKS5 = "SOCKS5"
    HTTP = "HTTP"


@unique
class ProxyStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    OK = "OK"
    DOWN = "DOWN"


class Group(MongoModel):
    __collection__ = "group"
    __indexes__ = ["!link", "created_at", "checked_at"]
    id: str = Field(..., alias="_id")
    link: HttpUrl
    username: str | None = None
    password: str | None = None
    port: int
    type: ProxyType
    created_at: datetime = Field(default_factory=utc_now)
    checked_at: datetime | None = None


class GroupCreate(BaseModel):
    name: str
    link: HttpUrl = None
    username: str | None = None
    password: str | None = None
    port: int
    type: ProxyType


class Proxy(MongoModel):
    __collection__ = "proxy"
    __indexes__ = ["!host", "group", "status", "type", "created_at", "checked_at", "last_ok_at"]
    id: ObjectIdStr | None = Field(None, alias="_id")
    group: str
    type: ProxyType
    status: ProxyStatus = ProxyStatus.UNKNOWN
    username: str
    password: str
    host: str
    port: int
    created_at: datetime = Field(default_factory=utc_now)
    checked_at: datetime | None = None
    last_ok_at: datetime | None = None

    @property
    def url(self):
        schema = "socks5" if self.type == ProxyType.SOCKS5 else "http"
        return f"{schema}://{self.username}:{self.password}@{self.host}:{self.port}"

    def delete_me(self) -> bool:
        if self.last_ok_at and self.last_ok_at > utc_delta(hours=-1):
            return False
        if self.created_at > utc_delta(hours=-1):
            return False
        return True

    @classmethod
    def from_group(cls, group: Group, host: str) -> Proxy:
        return Proxy(
            group=group.id,
            type=group.type,
            username=group.username,
            password=group.password,
            host=host,
            port=group.port,
        )
