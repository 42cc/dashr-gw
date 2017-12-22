import React from "react";
import Button from 'react-bootstrap/lib/Button';
import Col from 'react-bootstrap/lib/Col';
import Panel from 'react-bootstrap/lib/Panel';

export default class Home extends React.Component {

    render() {
        return (
            <Col sm={6} smOffset={3}>
                <Panel bsStyle="default" className="panel-wrapper panel-wrapper-main-menu">
                    <Button bsStyle="default" className="btn-landing" href="/deposit/">
                        Deposit DASH to Ripple
                    </Button>
                    <Button bsStyle="default" className="btn-landing" href="/withdraw/">
                        Withdraw DASH from Ripple
                    </Button>
                </Panel>
            </Col>
        );
    }
}
