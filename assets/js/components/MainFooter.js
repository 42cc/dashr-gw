import React from "react";

export default class Footer extends React.Component {
    render() {
        let year = new Date().getFullYear();
        return (
            <footer className="footer navbar-default">
                <div className="container">
                    <div className="row">
                        <div className="col-xs-12">
                            &copy; DASH Ripple Gateway {year}.
                        </div>
                    </div>
                </div>
            </footer>
        )
    }
}