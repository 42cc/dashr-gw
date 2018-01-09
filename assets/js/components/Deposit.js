import React from "react";
import DjangoCSRFToken from 'django-react-csrftoken';
import Button from 'react-bootstrap/lib/Button';
import Panel from 'react-bootstrap/lib/Panel';
import Form from 'react-bootstrap/lib/Form';
import FormGroup from 'react-bootstrap/lib/FormGroup';
import FormControl from 'react-bootstrap/lib/FormControl';
import ControlLabel from 'react-bootstrap/lib/ControlLabel';
import HelpBlock from 'react-bootstrap/lib/HelpBlock';
import Col from 'react-bootstrap/lib/Col';

import Transaction from './Transaction';

export default class Deposit extends Transaction {
    constructor(props) {
        super(props);
        this.transactionType = 'deposit';
    }

    render() {
        if (this.state && this.state.dashWallet && this.state.statusUrl) {
            return (
                <Panel bsStyle="default" className="panel-wrapper panel-wrapper-container">
                    <Col sm={12} md={6}>
                        <b>You have initiated a transaction from Dash to Ripple</b>
                        <p>
                            <span>Please transfer </span>
                            <b>{this.state.dashToTransfer} </b>
                            <span>DASH to this address: </span>
                            <b>{this.state.dashWallet} </b>
                        </p>
                        <p>
                            <span>You can track status of this transaction </span>
                            <a href={this.state.statusUrl}>here</a>.
                        </p>
                    </Col>
                </Panel>
            )
        }
        return (
            <Panel header="Deposit DASH to Ripple" bsStyle="default"
                   className="panel-wrapper panel-wrapper-container">
                <Col sm={12} md={6}>
                    <Form onSubmit={this.handleFormSubmit.bind(this)} id="deposit-form">
                        <DjangoCSRFToken/>
                        <FormGroup controlId="ripple_address_input"
                                   validationState={this.getFieldValidationState('ripple_address')}>
                            <ControlLabel>Your Ripple Address:</ControlLabel>
                            <FormControl type="text" name="ripple_address" required />
                            {this.getFieldError('ripple_address')}
                            <FormControl.Feedback />
                        </FormGroup>
                        <FormGroup controlId="dash_to_transfer_input"
                                   validationState={this.getFieldValidationState('dash_to_transfer')}>
                            <ControlLabel>
                                Deposit Amount (Min. {this.state.minAmount} DASH):
                            </ControlLabel>
                            <FormControl type="number"
                                         name="dash_to_transfer"
                                         onInput={this.changeReceiveAmountField.bind(this)}
                                         step="0.00000001"
                                         min={this.state.minAmount}
                                         required/>
                            {this.getFieldError('dash_to_transfer')}
                            <FormControl.Feedback />
                        </FormGroup>
                        <FormGroup id="receive-amount-form-group">
                            <ControlLabel>Receive Amount:</ControlLabel>
                            <FormControl id="dash_to_receive_input" disabled/>
                        </FormGroup>
                        <Button block type="submit">Start</Button>
                        <HelpBlock>
                            <Button bsStyle="link" href="/deposit/how-to/">Need help?</Button>
                        </HelpBlock>
                    </Form>
                </Col>
            </Panel>
        );
    }

    handleFormSubmit(event) {
        event.preventDefault();
        $('button[type="submit"]').prop('disabled', true);
        $.post(
            urls.submitDeposit,
            $('#deposit-form').serialize(),
        ).done((data) => {
            if (data.success) {
                this.setState({
                    dashWallet: data['dash_wallet'],
                    dashToTransfer: data['dash_to_transfer'],
                    statusUrl: data['status_url'],
                });
            } else {
                this.setState({formErrors: data['form_errors']});
            }
        }).always(() => {$('button[type="submit"]').prop('disabled', false);})
    }
}
