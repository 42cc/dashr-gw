import React from "react";
import Button from 'react-bootstrap/lib/Button';
import Panel from 'react-bootstrap/lib/Panel';
import Form from 'react-bootstrap/lib/Form';
import FormGroup from 'react-bootstrap/lib/FormGroup';
import FormControl from 'react-bootstrap/lib/FormControl';
import ControlLabel from 'react-bootstrap/lib/ControlLabel';
import HelpBlock from 'react-bootstrap/lib/HelpBlock';
import Col from 'react-bootstrap/lib/Col';
import InputGroup from 'react-bootstrap/lib/InputGroup';

export default class DepositDash extends React.Component {
    render() {
        const title = (
            <h3>Deposit DASH to</h3>
        )
        return (
            <Panel header={title} bsStyle="default"
                   className="panel-wrapper panel-wrapper-container">
                <Col sm={12} md={6}>
                    <Form>
                        <FormGroup controlId="id_ripple_address">
                            <Col md={12}>
                                <ControlLabel>Enter your ripple address, please:</ControlLabel>
                                <InputGroup>
                                    <FormControl type="text"/>
                                    <InputGroup.Button>
                                        <Button type="submit">Start</Button>
                                    </InputGroup.Button>
                                </InputGroup>
                                <FormControl.Feedback />
                                <HelpBlock>
                                    <Button bsStyle="link" href="#">Need help?</Button>
                                </HelpBlock>
                            </Col>
                        </FormGroup>
                    </Form>
                </Col>
            </Panel>
        );
    }
}
