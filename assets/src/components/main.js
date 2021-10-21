import React, { useState } from 'react'
import { Button } from 'semantic-ui-react'

// The /**/ before the function name is important.
// It serves as an annotation to export the react component to use in django.
/**/function ExampleReactComponent(props){
    let [counter, setCounter] = useState(props.count);
    return (
        <div>
            Test react component:
            <h2>{counter}</h2>
            <Button onClick={e => setCounter(counter+1)}>Increase</Button>
            <Button onClick={e => setCounter(counter-1)}>Decrease</Button>
        </div>
    )
}