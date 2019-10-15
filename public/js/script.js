
var myCarApp = angular.module('MyCarApp',['ngRoute'])

myCarApp.config(['$routeProvider', function($routeProvider){
    
  $routeProvider
    .when('/home',{
      templateUrl: 'views/carsTable.html',
      controller: 'TableController'
    }).when('/car',{
      templateUrl: 'views/carInfo.html',
      controller: 'CarController'
    }).otherwise({
      redirectTo: '/home'
    })
}])

myCarApp.controller('TableController',["$scope", "$http", '$rootScope',function($scope, $http, $rootScope){
  $http.get("http://localhost:27017/cars/")
  .then(function successCallback(response) {
      $scope.cars = response.data;
  });

  $scope.getCarData = function(car){
      var getCar = car._id
      $http.get("http://localhost:27017/cars/"+getCar)
      .then(function successCallback(response) {
        $rootScope.$broadcast('carGiven', response.data);
    });
  }

}]);

myCarApp.controller('CarController',["$scope", "$rootScope",function($scope, $rootScope){
  $rootScope.$on('carGiven', function(event, data){
    console.log(data)
    $scope.carData = data;
  });

}]);