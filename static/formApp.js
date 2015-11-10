
// create our angular app and inject ngAnimate and ui-router 
// =============================================================================
app = angular.module('formApp', ['ngAnimate', 'ui.router', 'ui.bootstrap',"angucomplete-alt"])

// ,
// configuring our routes 
// =============================================================================
app.config(function($stateProvider, $urlRouterProvider,$interpolateProvider) {

    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');

    $stateProvider
    
        // route to show our basic form (/form)
        .state('form', {
            url: '/form',
            templateUrl: '/form.html',
            controller: 'formController'
        })
        
        // nested states 
        // each of these sections will have their own view
        // url will be nested (/form/profile)
        .state('form.confirm', {
            url: '/confirm',
            templateUrl: 'form-confirm.html'
        })
        
        // url will be /form/interests
        .state('form.next', {
            url: '/next',
            templateUrl: 'form-next.html'
        })

        .state('form.info', {
            url: '/info',
            templateUrl: 'form-info.html'
        })
        .state('form.multi', {
            url: '/multi',
            templateUrl: 'form-multi.html'
        })
        .state('form.add', {
            url: '/add',
            templateUrl: 'form-add.html'
        })
        .state('form.members', {
            url: '/members?comId',
            templateUrl: 'form-members.html',
            controller: function($scope, $stateParams) {
              $scope.comId = $stateParams.comId;
            }
        })
        .state('form.coms', {
            url: '/coms',
            templateUrl: 'form-coms.html'
        })
        .state('form.create', {
            url: '/create',
            templateUrl: 'form-create.html'
        })
        .state('form.invite', {
            url: '/invite',
            templateUrl: 'form-invite.html'
        })
        .state('form.dash', {
            url: '/dash',
            templateUrl: 'dash.html'
        })
        .state('form.email', {
            url: '/email',
            templateUrl: 'form-email.html'
        })
        .state('form.remove', {
            url: '/remove',
            templateUrl: 'form-remove.html'
        })
        .state('form.done', {
            url: '/done',
            templateUrl: 'form-done.html'
        })
        .state('form.pay', {
            url: '/pay',
            templateUrl: 'form-pay.html'
        });

       
    // catch all route
    // send users to the form page 
    $urlRouterProvider.otherwise('/form/info');
})

// our controller for the form
// =============================================================================
app.controller('formController', function($scope,$http,$log, $state,$location) {
    
    window.setState = function(data) {
      $scope.$apply(function() {
        $scope.formData = data;
      })
    } 

    // we will store all of our form data in this object
    $scope.formData = {};
    $scope.multiData2=[];
    $scope.removeData = {};
    $scope.invites = {};
    $scope.invitesSO = {};
    $scope.newCom = {};
    $scope.recommendations = {};
    $scope.emails = ['me 1'];
    $scope.emailsSO = ['them 1'];
    
    $scope.$location = {};
    angular.forEach("protocol host port path search hash".split(" "), function(method){
     $scope.$location[method] = function(){
       var result = $location[method].call($location);
       return angular.isObject(result) ? angular.toJson(result) : result;
     };
    });

    $scope.$on("$stateChangeSuccess", function(event, toState) {
      updateIsOnForm(toState);
      updateIsOnForm2(toState);
      updateIsOnForm3(toState);
    })

    function updateIsOnForm(state) {
      $scope.isOnForm = ['form.confirm', 'form.multi'].indexOf(state.name) !== -1
                        ? "active"
                        : ""
    }

    function updateIsOnForm3(state) {
      $scope.isOnForm3 = ['form.info', 'form.remove'].indexOf(state.name) !== -1
                        ? "active"
                        : ""
    }

    function updateIsOnForm2(state) {
      $scope.isOnForm2 = ['form.done', 'form.next'].indexOf(state.name) !== -1
                        ? "active"
                        : ""
    }

    $scope.isOnForm = "";
    $scope.isOnForm2 = "";
    $scope.isOnForm3 = "";
    updateIsOnForm($state.current)
    updateIsOnForm2($state.current)
    updateIsOnForm3($state.current)

    $scope.setCoNaics = function(obj) {
      // console.log("Autoselect:", obj)
      $scope.formData.coNaics = obj.title
    }
    $scope.setCoSearch = function(obj) {
      // console.log("Autoselect:", obj)
      $scope.formData.coSearch = obj.title
    }



    $scope.addU = function ( text ) {
      data = $scope.formData;
      return $http({ 
                method: 'POST',
                headers: {
                  "Content-Type": "application/json"
                },
                data: data,
                url:"/add",
      }).then(function(result) {
        $state.go('form.next')
        
      }).catch(function(err){
        // console.log(err);
        $scope.usernameTaken=1
        $state.go('form.info')
      })
    };

    $scope.removeMe = function ( text ) {
      data = $scope.removeData;
      return $http({ 
                method: 'POST',
                headers: {
                  "Content-Type": "application/json"
                },
                data: data,
                url:"/remove_req",
      }).then(function(result) {
        $state.go('form.done')
        
      }).catch(function(err){
        // console.log(err);
      })
    };

    $scope.multiSubmit = function ( text ) {
      
      $scope.multiData2.push($scope.invites);
      $scope.multiData2.push($scope.invitesSO);
      data=$scope.multiData2;
      return $http({ 
                method: 'POST',
                headers: {
                  "Content-Type": "application/json"
                },
                data: data,
                url:"/multi",
      }).then(function(result) {
      if (result['data']['status'] == 'emailNotConfirmed') {
          $scope.confirmYourEmail=1;
          $state.go('form.multi');
      } else {
          $state.go('form.done');
      }
      }).catch(function(err){
        // console.log(err);
        $scope.confirmYourEmail=1;
        $state.go('form.multi');
      })
    };



    $scope.addEmail = function() {
      var newEmailNo = $scope.emails.length + 1;
      $scope.emails.push('me ' + newEmailNo);
    };

    $scope.addEmailSO = function() {
      var newEmailNo = $scope.emailsSO.length + 1;
      $scope.emailsSO.push('them ' + newEmailNo);
    };



    // function to submit the form after all validation has occurred            
    $scope.submitForm = function() {
      $state.go('form.confirm')
    };



    
}); // ############# end of formController ##################


app.controller('AccordionCtrl', function ($scope) {
  $scope.oneAtATime = true;

  $scope.groups = [
    {
      title: 'Dynamic Group Header - 1',
      content: 'Dynamic Group Body - 1'
    },
    {
      title: 'Dynamic Group Header - 2',
      content: 'Dynamic Group Body - 2'
    }
  ];

  $scope.status = {
    isFirstOpen: true,
    isFirstDisabled: false
  };
});

app.controller('popController', function ($scope, $sce) {
  $scope.popover = {
    content: 'Hello, World!',
    title: 'Title'
  };
});


app.controller('autoCompController', ['$scope', '$http',
  function autoCompController($scope, $http) {
    $scope.remoteUrlRequestFn = function(str) {
      return {q: str};
    };

    $scope.countrySelected = function(selected) {
      window.alert('You have selected ' + selected.title);
    };

    $scope.people = [
      {firstName: "Daryl", surname: "Rowland", twitter: "@darylrowland", pic: "img/daryl.jpeg"},
      {firstName: "Alan", surname: "Partridge", twitter: "@alangpartridge", pic: "img/alanp.jpg"},
      {firstName: "Annie", surname: "Rowland", twitter: "@anklesannie", pic: "img/annie.jpg"}
    ];

    $http.get("/search_naics2").success( function( data ) {
        $scope.naics = data;
    });

    $http.get("/get_coms").success( function( data ) {
        $scope.comSearch = data;
    });

    $scope.countrySelected9 = {name: 'Zimbabwe', code: 'ZW'};
    $scope.countrySelectedFn9 = function(selected) {
      if (selected) {
        $scope.countrySelected9 = selected.originalObject;
      } else {
        $scope.countrySelected9 = null;
      }
    }

    $scope.inputChanged = function(str) {
      $scope.console10 = str;
    }

    $scope.focusState = 'None';
    $scope.focusIn = function() {
      var focusInputElem = document.getElementById('ex12_value');
      $scope.focusState = 'In';
      focusInputElem.classList.remove('small-input');
    }
    $scope.focusOut = function() {
      var focusInputElem = document.getElementById('ex12_value');
      $scope.focusState = 'Out';
      focusInputElem.classList.add('small-input');
    }

    $scope.disableInput = true;
  }
]);


