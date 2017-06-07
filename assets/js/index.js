import React from 'react';
import {render} from 'react-dom'
import {BrowserRouter as Router, Route, Switch} from 'react-router-dom'

import Footer from "./components/MainFooter";
import Header from "./components/MainHeader";
import Home from "./components/Home";
import WithdrawDash from "./components/WithdrawDash";
import Page from "./components/Page";
import Wrapper from "./components/Wrapper";


class App extends React.Component {
    render() {
        return (
            <Router>
                <Wrapper>
                    <Header/>
                    <div className='container'>
                        <Switch>
                            <Route exact path="/" component={Home}/>
                            <Route path="/withdraw-dash/" component={WithdrawDash}/>
                            <Route path="/:slug/" component={Page}/>
                        </Switch>
                    </div>
                    <Footer/>
                </Wrapper>
            </Router>
        );
    }
}

render(<App />, document.getElementById('root'))