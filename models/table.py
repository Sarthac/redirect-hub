from datetime import datetime
from extensions import db
from helper.hash import get_hash, check_hash
from flask import jsonify


class Api(db.Model):
    __tablename__ = "api"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    api_key = db.Column(db.String, unique=True, nullable=False)
    created_by = db.Column(
        db.String, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<api_key {self.api_key}>"

    def delete_api_key(self):
        db.session.delete(self)
        db.session.commit()
        return True

    @classmethod
    def get_api_id(cls, api_key: str):
        hash_api_key = get_hash(api_key)
        return (
            cls.query.with_entities(cls.created_by)
            .filter_by(api_key=hash_api_key)
            .scalar()
        )


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<User {self.user_id}>"

    def delete_user(self):
        db.session.delete(self)
        db.session.commit()
        return True

    # @classmethod
    # def find_user_id(cls, user_id: str):
    #     hash_user_id = get_hash(user_id)
    #     if check_hash(hash_user_id, user_id):
    #         return cls.query.filter_by(user_id=hash_user_id).first()


class Redirect(db.Model):
    __tablename__ = "redirect"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    route = db.Column(db.String, unique=True, nullable=False)
    url = db.Column(db.String, nullable=False)
    created_by = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime)

    @classmethod
    def route_exists(cls, route: str):
        return cls.query.filter_by(route=route).first() is not None

    @classmethod
    def find_using_route_and_created_by(cls, route: str, created_by: int):
        result = cls.query.filter_by(route=route, created_by=created_by).first()
        return result
        # return True if result is not None else False

    # -----------
    # Actions
    # -----------

    @classmethod
    def create_route(cls, route: str, url: str, created_by=None):
        if not cls.route_exists(route):
            try:
                new_route = cls(route=route, url=url, created_by=created_by)
                db.session.add(new_route)
                db.session.commit()
                return True
            except Exception as e:
                db.session.rollback()
                return e
        return False

    @classmethod
    def user_routes(cls, created_by: int):
        entries = cls.query.filter_by(created_by=created_by).all()
        return [
            {
                "route": entry.route,
                "url": entry.url,
                "created_at": str(entry.created_at),
                "updated_at": str(entry.updated_at),
            }
            for entry in entries
        ]

    @classmethod
    def update_route(cls, existing_route: str, new_route: str, created_by: int):
        result = Redirect.query.filter(
            (cls.route == existing_route)
            & (cls.created_by == created_by)
            & (cls.route != new_route)
        ).first()

        if result:
            result.route = new_route
            result.created_at = datetime.now()
            db.session.commit()
            return True
        else:
            """
            which mean :
            1. 'route' does not exists
            2. owner does not own route or
            3. 'new_route' is alreday exists as a route.
            """
            return False

    @classmethod
    def delete_route(cls, routes: list, created_by: int):
        count_deleted_entry = 0
        count_entry_not_found = 0

        for route in routes:
            entry = cls.query.filter_by(route=route, created_by=created_by).first()
            if entry:
                db.session.delete(entry)
                count_deleted_entry += 1
            else:
                count_entry_not_found += 1

        # commit only if something was deleted
        if count_deleted_entry > 0:
            db.session.commit()

        return {
            "success": count_deleted_entry,
            "fail": count_entry_not_found,
        }

    # -------------
    # usage
    # -------------
    # redirect = Redirect.find_using_route_and_created_by("my-route", session["id"])
    # if redirect:
    #     redirect.update_url("https://new-url.com")
    #     # or
    #     redirect.delete()

    # Redirect.update_url("my-route", "https://new-url.com", session["id"])
    # Redirect.delete_route("my-route", session["id"])
