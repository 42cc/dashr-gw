import React from "react";
import Button from 'react-bootstrap/lib/Button';
import Col from 'react-bootstrap/lib/Col';
import Panel from 'react-bootstrap/lib/Panel';
import { LinkContainer } from 'react-router-bootstrap';

export default class Home extends React.Component {

    render() {
        return (
            <Col sm={6} smOffset={3}>
                <Panel className="panel-wrapper panel-wrapper-main-menu">
                    <Panel.Body>
                        <LinkContainer to="/deposit/">
                            <Button className="btn-landing">
                                Deposit DASH to Ripple
                            </Button>
                        </LinkContainer>
                        <LinkContainer to="/withdraw/">
                            <Button className="btn-landing">
                                Withdraw DASH from Ripple
                            </Button>
                        </LinkContainer>
                    </Panel.Body>
                </Panel>
            </Col>
        );
    }
}
