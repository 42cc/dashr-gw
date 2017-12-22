import Status from './Status';

export default class WithdrawStatus extends Status {
    constructor(props) {
        super(props);
        this.state.isDeposit = false;
    }
}
