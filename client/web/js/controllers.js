angular.module('rangevoting').controller('createRangeVoteController', ['$scope', '$location', 'Restangular', function ($scope, $location, Restangular) {
    $scope.isValid = true;

    $scope.rangevoteIsValid = function (rangevote) {
        return !!(rangevote.question && rangevote.choices.length > 1);
    };

    $scope.convertRangeVote = function (form) {
        var rangevote = {question: '', choices: []};
        if (form) {
            rangevote.question = form.question;
            rangevote.choices = _.map(form.choices.split(','), _.trim);
            return rangevote
        }
        return rangevote
    };

    var rangevotes = Restangular.all('rangevotes');

    $scope.createRangevote = function (form) {
        var rangevote = $scope.convertRangeVote(form);
        if ($scope.rangevoteIsValid(rangevote)) {
            rangevotes.post(rangevote).then(function (newRangevote) {
                $location.path('/rangevotes/' + newRangevote.id + '/admin/');
            });
        }
    }
}]);

angular.module('rangevoting').controller('adminRangeVoteController', ['$scope', '$routeParams', 'Restangular', function ($scope, $routeParams, Restangular) {
    $scope.rangevote = Restangular.one("rangevotes", $routeParams.id).get().then(function (rangevote) {
        $scope.rangevote = rangevote;
    });

    $scope.newChoice = '';
    $scope.addNewChoice = function () {
        $scope.rangevote.choices.push($scope.newChoice);
        $scope.newChoice = '';
    };

    $scope.deleteChoice = function (choices, index) {
        choices.splice(index, 1);
    };

    $scope.updateRangeVote = function () {
        $scope.rangevote.put().then(function () {
            new Notification({
                message: '<p>votre vote a été correctement mis à jour.</p>',
                ttl: 5000,
                type: 'success'
            }).show();
        }, function () {
            new Notification({
                message: "<p>Vote de valeur est temporairement indisponible :( Patientez quelques instants et essayez d'accéder de nouveau à la page.</p>",
                ttl: 20000,
                type: 'error'
            }).show();
        });
    };
}]);