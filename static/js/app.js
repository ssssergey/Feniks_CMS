'use strict';
var app = angular.module('appProducts', []);

app.config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});

app.controller('ProductsCtrl', function ($scope, $http) {
    $scope.items = [];
    
    $http.get('/api/products/').then(function (response) {
        $scope.items = response.data;
    });
    console.log($scope.items);

});


app.config([
    '$httpProvider', function ($httpProvider) {
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    }
]);