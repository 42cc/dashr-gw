import React from "react";
import { Navbar, Nav, NavItem, Button } from 'react-bootstrap'
import { LinkContainer } from 'react-router-bootstrap'


export default class Header extends React.Component {
    render() {
        return (
            <Navbar collapseOnSelect>
                <Navbar.Header>
                    <Navbar.Brand>
                        <LinkContainer to="/">
                            <Button bsStyle="link">Dash Ripple Gateway</Button>
                        </LinkContainer>
                    </Navbar.Brand>
                    <Navbar.Toggle />
                </Navbar.Header>
                <Navbar.Collapse>
                    <Nav pullRight>
                        <LinkContainer to="#">
                            <NavItem>FAQ</NavItem>
                        </LinkContainer>
                        <LinkContainer to="/about/">
                            <NavItem>About</NavItem>
                        </LinkContainer>
                        <LinkContainer to="/contact-us/">
                            <NavItem>Contact Us</NavItem>
                        </LinkContainer>
                        <LinkContainer to="/terms-and-conditions/">
                            <NavItem>Terms and Conditions</NavItem>
                        </LinkContainer>
                    </Nav>
                </Navbar.Collapse>
            </Navbar>
        )
    }
}