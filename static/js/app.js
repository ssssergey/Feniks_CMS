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

    $scope.product = {};
    $scope.create_product = function () {
        $http({
            url: '/api/products/create/',
            method: "POST",
            data: $scope.product
        })
            .success(function (data) {
                $scope.items.push(data);
            })
            .error(function (error, status) {
                $scope.errors = error.name[0];
            });
    }

})
;


app.config([
    '$httpProvider', function ($httpProvider) {
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    }
]);