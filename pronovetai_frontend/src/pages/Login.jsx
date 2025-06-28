import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Container, Row, Col, Card, Form, Button, Alert } from 'react-bootstrap';
import API from '../api';

export default function Login() {
  const navigate = useNavigate();
  const [form,  setForm]  = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [keep,  setKeep]  = useState(false);
  const [show,  setShow]  = useState(false);

  const handle = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const { data } = await API.post('token/', form);
      localStorage.setItem('accessToken',  data.access);
      localStorage.setItem('refreshToken', data.refresh);
      localStorage.setItem('username',     form.username);
      if (keep) localStorage.setItem('keepLoggedIn', '1');
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail ||
               err.response?.data?.non_field_errors?.[0] ||
               'Invalid credentials, please try again.');
    }
  };

  return (
    <Container fluid className="min-vh-100 d-flex align-items-center">
      <Row className="flex-grow-1 justify-content-center">
        <Col xs={12} md={6} lg={4}>
          <Card className="shadow-sm">
            <Card.Body>
              <h3 className="mb-3 text-center">Sign In</h3>
              {error && <Alert variant="danger">{error}</Alert>}

              <Form onSubmit={submit}>
                <Form.Group className="mb-3">
                  <Form.Label>Username</Form.Label>
                  <Form.Control name="username" value={form.username}
                                onChange={handle} required />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Password</Form.Label>
                  <Form.Control name="password"
                                type={show ? 'text' : 'password'}
                                value={form.password}
                                onChange={handle} required />
                  <Form.Check type="checkbox" label="Show password"
                              className="mt-1"
                              checked={show}
                              onChange={() => setShow(!show)}/>
                </Form.Group>

                <Form.Check type="checkbox" label="Keep me logged in"
                            className="mb-3"
                            checked={keep}
                            onChange={() => setKeep(!keep)}/>

                <Button type="submit" className="w-100">Sign In</Button>
              </Form>

              <hr />
              <div className="text-center">
                <small>Don’t have an account? <Link to="/register/staff">Sign up</Link></small>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}
