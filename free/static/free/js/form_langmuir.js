
/* To have a tab visible on page load, add the class active to both the initializing menu and the tab.
Please see semantic ui webpage*/


$(document).ready(function() {
    $('.item').tab();
  });
  // tab
  
   // Tensão desejada do sinal
   $('#range3').range({
      min: 10,
      max: 80,
      start: 20,
      input: '#Vsignal',
      labelType: 'letter'
    });
  
    // Periodo do snal de varrimento
   $('#range4').range({
      min: 8,
      max: 40,
      start: 25,
      input: '#Pvariment'
    });

     // Número de amostra por periodo
   $('#range5').range({
    min: 0,
    max: 40,
    start: 20,
    input: '#Nsamples',
    labelType: 'letter'
  });

  // Número de periodos
 $('#range6').range({
    min: 5,
    max: 50,
    start: 20,
    input: '#Nperiod'
  });

  // Número de periodos
 $('#range7').range({
    min: 0.0,
    max: 5.0,
    start: 3.0,
    input: '#Pgas'
  });

   // Número de periodos
 $('#range8').range({
    min: 0.0,
    max: 5.0,
    start: 0.1,
    input: '#Pbomba'
  });
  
  
 
      