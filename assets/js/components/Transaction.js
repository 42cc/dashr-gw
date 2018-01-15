import React from "react";
import Decimal from "decimal.js/decimal";
import HelpBlock from 'react-bootstrap/lib/HelpBlock';

export default class Transaction extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            minAmount: '0.00000001',
        };
    }

    componentDidMount() {
        window.addEventListener('load', () => {
            this.setState({minAmount: minAmounts[this.transactionType]});
        })
    }

    handleFormSubmit(event) {
        event.preventDefault();
        $('button[type="submit"]').prop('disabled', true);
        $.post(
            urls.submit[this.transactionType],
            $('#transaction-form').serialize(),
        ).done(data => {
            this.setState({statusUrl: data['status_url']});
        }).fail(xhr => {
            if (xhr.status === 400) {
                this.setState({formErrors: xhr.responseJSON['form_errors']});
            }
        }).always(() => {$('button[type="submit"]').prop('disabled', false);})
    }

    hasErrorsField(fieldName) {
        return (this.state.formErrors && this.state.formErrors[fieldName]);
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
        const amount = new Decimal($amountField.val());
        // Truncate amount to 8 decimal places.
        const truncatedAmount = amount.toDecimalPlaces(8);

        if (!amount.equals(truncatedAmount)) {
            $amountField.val(truncatedAmount);
        }

        // Set received amount.
        if (truncatedAmount < Decimal(this.state.minAmount)) {
            $receiveAmountField.val(0);
            return;
        }
        $.getJSON(
            urls.getReceivedAmount,
            {'amount': truncatedAmount.toString(), 'transaction_type': this.transactionType},
        ).done((data) => {
            $receiveAmountField.val(Decimal(data['received_amount']));
        });
    }
}
