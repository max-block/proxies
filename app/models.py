from __future__ import annotations

from datetime import datetime
from enum import Enum, unique

from mb_std import utc_delta, utc_now
from mb_std.mongo import MongoModel, ObjectIdStr
from pydantic import BaseModel, Field, HttpUrl
from pymongo import IndexModel


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
    id: ObjectIdStr | None = Field(None, alias="_id")
    name: str
    link: HttpUrl
    username: str | None = None
    password: str | None = None
    port: int
    type: ProxyType
    created_at: datetime = Field(default_factory=utc_now)
    checked_at: datetime | None

    __collection__ = "group"
    __indexes__ = [
        IndexModel("name", unique=True),
        IndexModel("link", unique=True),
        IndexModel("created_at"),
        IndexModel("checked_at"),
    ]


class GroupCreate(BaseModel):
    name: str
    link: HttpUrl = None
    username: str | None = None
    password: str | None = None
    port: int
    type: ProxyType


class Proxy(MongoModel):
    __collection__ = "proxy"
    __indexes__ = [
        IndexModel("host", unique=True),
        IndexModel("group"),
        IndexModel("status"),
        IndexModel("type"),
        IndexModel("created_at"),
        IndexModel("checked_at"),
        IndexModel("last_ok_at"),
    ]
    id: ObjectIdStr | None = Field(None, alias="_id")
    group: str  # Group.name
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
            group=group.name,
            type=group.type,
            username=group.username,
            password=group.password,
            host=host,
            port=group.port,
        )
