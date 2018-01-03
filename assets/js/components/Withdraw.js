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
import Decimal from 'decimal.js';

export default class DepositDash extends React.Component {
    render() {
        if (this.state && this.state.rippleAddress && this.state.statusUrl) {
            return (
                <Panel bsStyle="default" className="panel-wrapper panel-wrapper-container">
                    <Col sm={12} md={6}>
                        <b>You have initiated a transaction from Ripple to Dash</b>
                        <p>
                            <span>Please transfer </span>
                            <b>{this.state.dashToTransfer} </b>
                            <span>Ripple token{this.state.dashToTransfer == 1 ? null : 's'} with a destination tag </span>
                            <b>{this.state.destinationTag} </b>
                            <span>to this address: </span>
                            <b>{this.state.rippleAddress} </b>
                        </p>
                        <p>
                            You can track status of this transaction
                            {' '}
                            <a href={this.state.statusUrl}>here</a>.
                        </p>
                    </Col>
                </Panel>
            )
        }
        return (
            <Panel header="Withdraw DASH from Ripple" bsStyle="default"
                   className="panel-wrapper panel-wrapper-container">
                <Col sm={12} md={6}>
                    <Form onSubmit={this.handleFormSubmit.bind(this)} id="withdrawal-form">
                        <DjangoCSRFToken/>
                        <FormGroup controlId="dash_address_input"
                                   validationState={this.getFieldValidationState('dash_address')}>
                            <ControlLabel>Your Dash Address:</ControlLabel>
                            <FormControl type="text" name="dash_address" required />
                            {this.getFieldError('dash_address')}
                            <FormControl.Feedback />
                        </FormGroup>
                        <FormGroup controlId="dash_to_transfer_input"
                                   validationState={this.getFieldValidationState('dash_to_transfer')}>
                            <ControlLabel>Withdrawal Amount:</ControlLabel>
                            <FormControl type="number"
                                         name="dash_to_transfer"
                                         onInput={this.changeReceiveAmountField}
                                         step="0.00000001"
                                         min="0.00000001"
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
                            <Button bsStyle="link" href="/withdraw/how-to/">Need help?</Button>
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
            urls.submitWithdrawal,
            $('#withdrawal-form').serialize(),
        ).done((data) => {
            if (data.success) {
                this.setState({
                    rippleAddress: data['ripple_address'],
                    destinationTag: data['destination_tag'],
                    dashToTransfer: data['dash_to_transfer'],
                    statusUrl: data['status_url'],
                });
            } else {
                this.setState({formErrors: data['form_errors']});
            }
        }).always(() => {$('button[type="submit"]').prop('disabled', false);})
    }

    hasErrorsField(fieldName) {
        return (this.state && this.state.formErrors[fieldName]);
    }

    getFieldError(fieldName) {
        if (this.hasErrorsField(fieldName)) {
            return (
                <HelpBlock>{this.state.formErrors[fieldName][0]}</HelpBlock>
            );
        }
    }

    getFieldValidationState(fieldName) {
        if (this.hasErrorsField(fieldName)) {
            return "error";
        }
    }

    changeReceiveAmountField(event) {
        const $amountField = $(event.target);
        const $receiveAmountField = $('#dash_to_receive_input');
        if (!$amountField.val()) {
            $receiveAmountField.val('');
            return;
        }

        Decimal.set({
            rounding: Decimal.ROUND_DOWN,
            toExpNeg: -9,
        });
        let amount = new Decimal($amountField.val());
        // Truncate amount to 8 decimal places.
        amount = amount.toDecimalPlaces(8);

        $amountField.val(amount);

        // Set received amount.
        $.getJSON(urls.getDashReceivedAmount, {'amount': amount.toString()}).done((data) => {
            $receiveAmountField.val(Decimal(data['received_amount']));
        });
    }
}
