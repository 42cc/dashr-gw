import React from 'react';
import {render} from 'react-dom'
import {BrowserRouter as Router, Route, Switch} from 'react-router-dom'

import Footer from "./components/MainFooter";
import Header from "./components/MainHeader";
import Home from "./components/Home";
import Deposit from "./components/Deposit";
import DepositStatus from "./components/DepositStatus";
import Withdraw from "./components/Withdraw";
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

                            <Route exact path="/deposit/" component={Deposit}/>
                            <Route exact path="/withdraw/" component={Withdraw}/>

                            <Route path="/deposit/:transactionId/status/"
                                   component={DepositStatus}/>

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