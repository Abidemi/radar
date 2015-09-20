from flask import request

from radar.api.serializers.users import UserSerializer, UserListRequestSerializer
from radar.lib.user_search import UserQueryBuilder
from radar.lib.views.core import ListCreateModelView, RetrieveUpdateDestroyModelView
from radar.lib.models import User
from radar.lib.auth.sessions import current_user


class UserListView(ListCreateModelView):
    serializer_class = UserSerializer
    model_class = User
    sort_fields = ('id', 'username', 'email', 'first_name', 'last_name')

    def get_query(self):
        serializer = UserListRequestSerializer()
        args = serializer.args_to_value(request.args)

        builder = UserQueryBuilder(current_user)

        if args.get('id') is not None:
            builder.user_id(args['id'])

        if args.get('username'):
            builder.username(args['username'])

        if args.get('email'):
            builder.email(args['email'])

        if args.get('first_name'):
            builder.first_name(args['first_name'])

        if args.get('last_name'):
            builder.last_name(args['last_name'])

        if args.get('cohort') is not None:
            builder.cohort(args['cohort'])

        if args.get('organisation') is not None:
            builder.organisation(args['organisation'])

        query = builder.build()

        return query


class UserDetailView(RetrieveUpdateDestroyModelView):
    serializer_class = UserSerializer
    model_class = User
