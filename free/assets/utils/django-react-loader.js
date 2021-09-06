function createAppendix(name) {
    return (
      "\n window.reactComponents." + name + " = (function() {               \n\
      let _args = {}                                                        \n\
                                                                            \n\
      return {                                                              \n\
        init: function (Args) {                                             \n\
          _args = Args                                                      \n\
        },                                                                  \n\
        render: function () {                                               \n\
          const  { id, ...props } = JSON.parse(_args)                       \n\
          render(<" + name + " {...props}/>, document.getElementById(id))   \n\
        }                                                                   \n\
      }                                                                     \n\
    }())"
    )
  }
  
module.exports = function djangoReactLoader(source) {
    var result = String(source);
    result = result.concat(
    "\n import { render } from 'react-dom'                                \n\
    if (window.reactComponents === undefined) {                           \n\
      window.reactComponents = {}                                         \n\
    }                                                                     \n\
    ");
    var regexp = /class (.*) extends React.Component/g;
    var match = regexp.exec(source);
    while (match!=null) {
        result = result.concat(createAppendix(match[1]));
        match = regexp.exec(source);
    }

    // To export function component you need to prefix it with  "/**/"
    var regexpFunc = /\/\*\*\/function ([^( ]*)\(/g;
    var matchFunc = regexpFunc.exec(source);
    while (matchFunc!=null) {
        result = result.concat(createAppendix(matchFunc[1]));
        matchFunc = regexpFunc.exec(source);
    }
    return result;
}