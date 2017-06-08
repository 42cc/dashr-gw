import React from "react";
import Button from 'react-bootstrap/lib/Button';
import Panel from 'react-bootstrap/lib/Panel';

export default class Home extends React.Component {

    render() {
        return (
            <Panel bsStyle="default" className="panel-wrapper panel-wrapper-main-menu">
                <Button bsStyle="default" className="btn-landing" href="/deposit-dash/">
                    Deposit DASH to Ripple
                </Button>
                <Button bsStyle="default" className="btn-landing" href="#">
                    Withdraw DASH from Ripple
                </Button>
            </Panel>
        );
    }
}
