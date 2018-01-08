import React from 'react';
import {render} from 'react-dom'
import {BrowserRouter as Router, Route, Switch} from 'react-router-dom'

import Footer from "./components/MainFooter";
import Header from "./components/MainHeader";
import Home from "./components/Home";
import Deposit from "./components/Deposit";
import Withdraw from "./components/Withdraw";
import Page from "./components/Page";
import Status from "./components/Status";
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

                            <Route exact path="/deposit/" component={Deposit}/>
                            <Route exact path="/withdraw/" component={Withdraw}/>

                            <Route path="/deposit/:transactionId([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/"
                                   component={props => <Status {...props} transactionType='Deposit'/>}/>
                            <Route path="/withdraw/:transactionId(\d+)/"
                                   component={props => <Status {...props} transactionType='Withdrawal'/>}/>

                            <Route path="/:slug/how-to/"
                                   component={props => <Page {...props} wrapped='true'/>}/>
                            <Route path="/:slug/"
                                   component={props => <Page {...props} wrapped='false' />} />


                        </Switch>
                    </div>
                    <Footer/>
                </Wrapper>
            </Router>
        );
    }
}

render(<App />, document.getElementById('root'))