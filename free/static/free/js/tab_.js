
/* To have a tab visible on page load, add the class active to both the initializing menu and the tab.
Please see semantic ui webpage*/

// tab
$('.menu .item').tab();  

// console.log('Tab List : ', exp_parameters);


if (exp_parameters.length > 0) {
 // Initial displacement
 $('#range1').range({
     min: parseInt (exp_parameters[0].min_val),
     max: parseInt (exp_parameters[0].max_val),
     step: parseInt (exp_parameters[0].step),
     start: parseInt (exp_parameters[0].start),
     input: '#'+exp_parameters[0].nome
 });
}

if (exp_parameters.length > 1) {
 // Number of samples
 $('#range2').range({
     min: parseInt (exp_parameters[1].min_val),
     max: parseInt (exp_parameters[1].max_val),
     step: parseInt (exp_parameters[1].step),
     start:  parseInt (exp_parameters[1].start),
     input: '#'+exp_parameters[1].nome
   });
}

// Initial displacement
//  $('#range1').range({
//     min: 0,
//     max: 20,
//     start: 1,
//     input: '#DeltaX'
//   });

// Number of samples
//  $('#range2').range({
//     min: 0,
//     max: 400,
//     start: 33,
//     input: '#Samples'
//   });



 $(document).ready(function(){
   $('.url.video .ui.embed').embed();

});

   