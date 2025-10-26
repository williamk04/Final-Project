import { BrowserRouter as Router, Link } from "react-router-dom";
import AppRoutes from "./routes/AppRoutes";
import { Navbar, Nav, Container } from "react-bootstrap";

function App() {
  return (
    <Router>
      <Navbar bg="dark" variant="dark" expand="lg">
        <Container>
          <Navbar.Brand as={Link} to="/">Smart Parking</Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="me-auto">
              <Nav.Link as={Link} to="/">Dashboard</Nav.Link>
              <Nav.Link as={Link} to="/history">Vehicle History</Nav.Link>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Container style={{ marginTop: "20px" }}>
        <AppRoutes />
      </Container>
    </Router>
  );
}

export default App;
