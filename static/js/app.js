'use strict';
var app = angular.module('app', ['ui.bootstrap']);

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
                $scope.items.unshift(data);
            })
            .error(function (error, status) {
                $scope.errors = error.name[0];
            });
    }
});

app.config([
    '$httpProvider', function ($httpProvider) {
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    }
]);


var buh_app = angular.module('accountant', ['ui.router', 'ui.bootstrap']);

buh_app.config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});

buh_app.config(function ($stateProvider, $urlRouterProvider) {
    $stateProvider
        .state('app', {
            url: '/',
            views: {
                'content@': {
                    templateUrl: 'static/ng-views/accountant/workers.html',
                    controller: 'OrdersCtrl'
                }
            }
        })
        .state('app.money', {
            url: 'money',
            views: {
                'content@': {
                    templateUrl: 'static/ng-views/accountant/money.html',
                    controller: 'MoneyCtrl'
                }
            }
        });
    $urlRouterProvider.otherwise('/');

});

buh_app.controller('OrdersCtrl', function ($scope, $http) {
    // Datepicker
    $scope.clear_from = function () {
        $scope.date_from = null;
    };
    $scope.clear_to = function () {
        $scope.date_to = null;
    };
    $scope.options = {
        showWeeks: true
    };

    $scope.users = [];

    $http.get('/api/users/').then(function (response) {
        $scope.users = response.data;
    });

    // $http.get('/api/orders/').then(function (response) {
    //     $scope.total_sub = response.data['total_sum'];
    //     $scope.orders = response.data['orders'];
    // });

    $scope.submit = function () {
        // if ($scope.date_from) {
        //     $scope.list.push(this.date_from.toISOString().slice(0, 10));
        //     $scope.date_from = '';}
        
        $scope.total_sum_for_salers = 0;
        $scope.total_sum_per_saler = 0;
        $scope.orders = [];

        $scope.total_sum_for_lifers = 0;
        $scope.total_sum_per_lifter = 0;
        $scope.deliveries = [];
        $scope.count_deliveries = 0;

        $scope.extra_deliveries = 0;
        $scope.full_days = 0;
        $scope.not_full_days = 0;
        $scope.dates = [];

        $scope.total_sum_for_assembling = 0;
        $scope.deliveries = [];
        $scope.count_deliveries = 0;
        
        $scope.show_manager = false;
        $scope.show_lifter = false;
        $scope.show_driver = false;
        $scope.show_assembler = false;


        var url_options = '';
        if (this.user) {
            url_options += 'saler=' + this.user + '&';
            url_options += 'lifter=' + this.user + '&';
            url_options += 'driver=' + this.user + '&';
        }
        if (this.date_from) {
            var date_from = this.date_from.getFullYear() + '-' + (parseInt(this.date_from.getMonth()) + 1) + '-' + this.date_from.getDate();
            url_options += 'date_from=' + date_from + '&';
        } else {
            $scope.error_1 = 'Пожалуйста, укажите начальную дату!';
            return
        }
        if (this.date_to) {
            var date_to = this.date_to.getFullYear() + '-' + (parseInt(this.date_to.getMonth()) + 1) + '-' + this.date_to.getDate();
            url_options += 'date_to=' + date_to + '&';
        } else {
            $scope.error_1 = 'Пожалуйста, укажите конечную дату!';
            return
        }

        if (url_options == '') {
            $scope.error_1 = 'Пожалуйста, ограничте запрос по времени!';
        } else {
            $scope.error_1 = 'Ожидайте...Идет загрузка...';
            $http.get('/api/orders-for-salers/?' + url_options).then(function (response) {
                $scope.error_1 = '';
                $scope.orders = response.data['orders'];
                $scope.total_sum_for_salers = response.data['total_sum_for_salers'];
                $scope.total_sum_per_saler = response.data['total_sum_per_saler'];
                if ($scope.orders.length > 0) $scope.show_manager = true;
            });
            $http.get('/api/delivery-lifter/?' + url_options).then(function (response) {
                $scope.error_1 = '';
                $scope.deliveries = response.data['deliveries'];
                $scope.count_deliveries = response.data['count'];
                $scope.total_sum_for_lifers = response.data['total_sum'];
                $scope.total_sum_per_lifter = response.data['total_sum_per_lifter'];
                if ($scope.deliveries.length > 0) $scope.show_lifter = true;
            });
            $http.get('/api/delivery-driver/?' + url_options).then(function (response) {
                $scope.error_1 = '';
                $scope.extra_deliveries = response.data['extra_deliveries'];
                $scope.full_days = response.data['full_days'];
                $scope.not_full_days = response.data['not_full_days'];
                $scope.dates = response.data['dates'];
                $scope.error_3 = response.data['error'];
                if ($scope.dates.length > 0) $scope.show_driver = true;
            });
                $http.get('/api/delivery-assembler/?' + url_options).then(function (response) {
                $scope.error_1 = '';
                $scope.assemblies = response.data['deliveries'];
                $scope.count_assemblies = response.data['count'];
                $scope.total_sum_for_assemblers = response.data['total_sum'];
                $scope.total_sum_with_discount = response.data['total_sum_with_discount'];
                if ($scope.assemblies.length > 0) $scope.show_assembler = true;
            });
        }
    };
});

buh_app.controller('MoneyCtrl', function ($scope, $http) {
    $scope.preload = 'Ожидайте...Идет загрузка...';
    $http.get('/api/money-extra/').then(function (response) {
        $scope.total_sum = response.data['total_sum'];
        $scope.total_sum_paid_not_delivered = response.data['total_sum_paid_not_delivered'];
        $scope.total_sum_partialy_paid = response.data['total_sum_partialy_paid'];
        $scope.orders = response.data['orders'];
        $scope.preload = '';
    });

});

buh_app.config([
    '$httpProvider', function ($httpProvider) {
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    }
]);