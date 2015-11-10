
// create our angular app and inject ngAnimate and ui-router 
// =============================================================================
app = angular.module('faqApp', ['ngAnimate', 'ui.router','ui.bootstrap',"angucomplete-alt"])


// configuring our routes 
// =============================================================================
app.config(function($stateProvider, $urlRouterProvider,$interpolateProvider) {

    $interpolateProvider.startSymbol('{[');
    $interpolateProvider.endSymbol(']}');

    // $stateProvider
    
    //     // route to show our basic form (/form)
    //     .state('about', {
    //         url: '/',
    //         templateUrl: 'about.html'
    //     })
        
    //     // nested states 
    //     // each of these sections will have their own view
    //     // url will be nested (/form/profile)
    //     .state('login', {
    //         url: '/login',
    //         templateUrl: 'login.html',
    //         controller: 'loginController'
    //     })
        
    //     // url will be /form/interests
    //     .state('profile', {
    //         url: '/profile',
    //         templateUrl: 'profile.html'
    //     })

    //     .state('stories', {
    //         url: '/stories',
    //         templateUrl: 'stories.html',
    //     });
    // $urlRouterProvider.otherwise('/stories');

})

// our controller for the form
// =============================================================================
app.controller('faqController', function($scope,$http,$log,$location) {

  $scope.faqData = {};
  $scope.storyData = {};
  $scope.newStory = {};
  $scope.status2 = {};
  $scope.oneAtATime = true;
  $scope.tellFlag = -1;

  $scope.openCloseId = function(id) {
      // console.log("index:", id)
      if ($scope.status2[id]) {
        // console.log("tested true1:", id, $scope.status2[id])
        $scope.status2[id] = false;
        // console.log("tested true2:", id, $scope.status2[id])
        
      } else  {
        $scope.status2[id] = true;
          for (stat in $scope.status2) {
              $scope.status2[stat] = false;
          }

        // console.log("tested true:", id)
      }
      return $scope.status2[id];
    }
  $http.get("/search_faq").success( function( data ) {
        $scope.faqs = data;
    });
  $http.get("/search_stories").success( function( data ) {
        $scope.stories = data;
    });
  $http.get("/get_user").success( function( data ) {
        $scope.username = data['username'];
    });
  $scope.setUp = function(id) {
        $scope.faqs[id].upvotes=$scope.faqs[id].upvotes+1
    };
  $scope.setDown = function(id) {
      $scope.faqs[id].downvotes=$scope.faqs[id].downvotes+1
      $scope.thisDown=true
  };
  $scope.voteStory = function(id,upDown) {
        data={'id':id, 'upDown':upDown}
        return $http({ 
                method: 'POST',
                headers: {
                  "Content-Type": "application/json"
                },
                data: data,
                url:"/post_votes"
                })
    }; 
    $scope.subFeed = function(id) {
        $scope.thisDown=false
    };
  $scope.tell = function() {
    $scope.tellFlag = $scope.tellFlag*-1;
    };
  $scope.postStory = function ( text ) {
      data = $scope.storyData;
      return $http({ 
                method: 'POST',
                headers: {
                  "Content-Type": "application/json"
                },
                data: data,
                url:"/post_story"
      }).then(function(result) {
        $scope.tellFlag = $scope.tellFlag*-1;
        }
      ).catch(function(err){
        console.log(err);
      });
  };
});

app.controller('loginController', function($scope,$http,$log,$location, $state, $window) {
  $scope.loginData = {};
  $scope.loginStatus = 0;
  $scope.readdData = {};

  $scope.login = function ( text ) {
      data = $scope.loginData;
      return $http({ 
                method: 'POST',
                headers: {
                  "Content-Type": "application/json"
                },
                data: data,
                url:"/login_req"
      }).then(function(result) {
        loginStatus = result.data['loginStatus'];
        $scope.loginStatus = loginStatus;
        // console.log("login status", loginStatus);
        if (loginStatus > 0) {
          // console.log("send to somewhere ", loginStatus);
          $window.location.assign('/stories');
        }
        
      }).catch(function(err){
        console.log(err);
      })
    };
  $scope.readd = function ( text ) {
      data = $scope.readdData;
      // console.log("emails", data);
      return $http({ 
                method: 'POST',
                headers: {
                  "Content-Type": "application/json"
                },
                data: data,
                url:"/readd"
      }).then(function(result) {
        // console.log("results", result);
      }).catch(function(err){
        // console.log(err);
      })
    };
  $scope.remove = function ( text ) {
      // data = $scope.loginData;
      return $http({ 
                method: 'POST',
                headers: {
                  "Content-Type": "application/json"
                },
                url:"/remove_req"
      }).then(function(result) {
        $window.location.assign('/about');
      }).catch(function(err){
        // console.log(err);
      })
    };





  });

