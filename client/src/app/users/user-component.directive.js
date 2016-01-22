(function() {
  'use strict';

  var app = angular.module('radar.users');

  app.factory('UserPermission', ['hasPermissionForUser', 'session', function(hasPermissionForUser, session) {
    function UserPermission() {
    }

    UserPermission.prototype.hasPermission = function() {
      return true;
    };

    UserPermission.prototype.hasObjectPermission = function(obj) {
      return (
        obj.id !== session.user.id && // separate forms for changing your own details
        hasPermissionForUser(session.user, obj, 'EDIT_USER')
      );
    };

    return UserPermission;
  }]);

  function controllerFactory(
    ModelDetailController, $injector, UserPermission, DenyPermission, session
  ) {
    function UserController($scope) {
      var self = this;

      $injector.invoke(ModelDetailController, self, {
        $scope: $scope,
        params: {
          createPermission: new DenyPermission(),
          editPermission: new UserPermission(),
          removePermission: new DenyPermission(),
        }
      });

      $scope.currentUser = session.user;

      self.load($scope.user).then(function() {
        self.view();
      });
    }

    UserController.$inject = ['$scope'];
    UserController.prototype = Object.create(ModelDetailController.prototype);

    UserController.prototype.save = function() {
      // If the password is blank don't update it
      if (!this.scope.item.password) {
        this.scope.item.password = undefined;
      }

      return ModelDetailController.prototype.save.call(this);
    };

    return UserController;
  }

  controllerFactory.$inject = [
    'ModelDetailController', '$injector', 'UserPermission', 'DenyPermission', 'session'
  ];

  app.factory('UserController', controllerFactory);

  app.directive('userComponent', ['UserController', function(UserController) {
    return {
      scope: {
        user: '='
      },
      controller: UserController,
      templateUrl: 'app/users/user-component.html'
    };
  }]);
})();
