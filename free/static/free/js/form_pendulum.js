
/* To have a tab visible on page load, add the class active to both the initializing menu and the tab.
Please see semantic ui webpage*/


$(document).ready(function() {
  $('.item').tab();
});
// tab

 // Initial displacement
 $('#range1').range({
    min: 5,
    max: 20,
    start: 10,
    input: '#DeltaX',
    labelType: 'letter'
  });

  // Nnumber of samples
 $('#range2').range({
    min: 10,
    max: 500,
    start: 100,
    input: '#Samples'
  });


  //////////////////////////////////////////////
  // Default setting
  



  $(document).ready(function(){
    $('.url.video .ui.embed').embed();

 });

 $('.ui.button')
 .on('click', function() {
   // programmatically activating tab
   $.tab('change tab', 'tab-name');
 })
;

    