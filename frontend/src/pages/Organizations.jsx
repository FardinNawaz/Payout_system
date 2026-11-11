
import { useEffect, useState } from "react";
import axios from "axios";
import { Search, Building2, KeyRound,Wallet,HandCoins } from "lucide-react";
import "./Organizations.css";

function Organizations() {
  const [organizations, setOrganizations] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [search, setSearch] = useState("");
  const [refresh, setRefresh] = useState(0);

  // Organization form states
  const [showForm, setShowForm] = useState(false);
  const [creating, setCreating] = useState(false);

  const [formData, setFormData] = useState({
    org_name: "",
    email: "",
    phone: "",
    password: ""
  });

  // API credentials form states
  const [showCredentialForm, setShowCredentialForm] =
    useState(false);

  const [selectedOrgId, setSelectedOrgId] = useState("");
  const [generatingCredentials, setGeneratingCredentials] =
    useState(false);

  const [credentials, setCredentials] = useState(null);

  const [showWalletForm, setShowWalletForm] = useState(false);
  const [selectedWalletOrgId, setSelectedWalletOrgId] = useState("");
  const [walletCurrency, setWalletCurrency] = useState("INR");
  const [creatingWallet, setCreatingWallet] = useState(false);
  const [wallet, setWallet] = useState(null);

  const [showCreditForm, setShowCreditForm] = useState(false);
  const [selectedCreditOrgId, setSelectedCreditOrgId] = useState("");
  const [creditAmount, setCreditAmount] = useState("");
  const [creditDescription, setCreditDescription] = useState("");
  const [addingBalance, setAddingBalance] = useState(false);
  const [creditResult, setCreditResult] = useState(null);


  const [showWalletStatusForm, setShowWalletStatusForm] = useState(false);
  const [selectedWalletStatusOrgId, setSelectedWalletStatusOrgId] = useState("");
  const [walletStatus, setWalletStatus] = useState("true");
  const [updatingWalletStatus, setUpdatingWalletStatus] = useState(false);

  const [showOrgStatusForm, setShowOrgStatusForm] = useState(false);
  const [selectedOrgStatusId, setSelectedOrgStatusId] = useState("");
  const [orgStatus, setOrgStatus] = useState("true");
  const [updatingOrgStatus, setUpdatingOrgStatus] = useState(false);


  const [showDetailsForm, setShowDetailsForm] = useState(false);
  const [selectedDetailsOrgId, setSelectedDetailsOrgId] = useState("");
  const [organizationDetails, setOrganizationDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  // =====================================
  // 1. FETCH ORGANIZATIONS
  // =====================================

  useEffect(() => {
    const fetchOrganizations = async () => {
      try {
        setLoading(true);
        setError("");

        const token = localStorage.getItem("access_token");

        const response = await axios.get(
          "http://127.0.0.1:8000/api/v1/admin/organizations",
          {
            headers: {
              access_token: token
            },
            params: {
              limit: 100,
              offset: 0,
              search: search || undefined
            }
          }
        );

        console.log("Organizations:", response.data);

        setOrganizations(response.data.data);

      } catch (error) {
        console.log(
          "Organizations error:",
          error.response?.data || error.message
        );

        setError(
          error.response?.data?.detail ||
          error.response?.data?.message ||
          "Unable to load organizations."
        );

      } finally {
        setLoading(false);
      }
    };

    fetchOrganizations();

  }, [search, refresh]);


  // =====================================
  // 2. CREATE ORGANIZATION
  // =====================================

  const handleCreateOrganization = async (e) => {
    e.preventDefault();

    try {
      setCreating(true);
      setError("");
      setSuccess("");
      setCredentials(null);

      const token = localStorage.getItem("access_token");

      const response = await axios.post(
        "http://127.0.0.1:8000/api/v1/admin/organizations/",
        formData,
        {
          headers: {
            access_token: token
          }
        }
      );

      console.log("Organization created:", response.data);

      setSuccess("Organization created successfully!");

      // Reset form
      setFormData({
        org_name: "",
        email: "",
        phone: "",
        password: ""
      });

      setShowForm(false);

      // Refresh organization list
      setRefresh((prev) => prev + 1);

    } catch (error) {
      console.log(
        "Create organization error:",
        error.response?.data || error.message
      );

      setError(
        error.response?.data?.detail ||
        error.response?.data?.message ||
        "Unable to create organization."
      );

    } finally {
      setCreating(false);
    }
  };


  // =====================================
  // 3. GENERATE API CREDENTIALS USING ORG ID
  // =====================================

  const handleGenerateCredentials = async (e) => {
    e.preventDefault();

    if (!selectedOrgId) {
      setError("Please select an organization.");
      return;
    }

    try {
      setGeneratingCredentials(true);
      setError("");
      setSuccess("");
      setCredentials(null);

      const token = localStorage.getItem("access_token");

      console.log("Selected Organization ID:", selectedOrgId);

      const response = await axios.post(
        `http://127.0.0.1:8000/api/v1/admin/organizations/${selectedOrgId}/api-credentials`,
        {},
        {
          headers: {
            access_token: token
          }
        }
      );

      console.log("Generated credentials:", response.data);

      setCredentials(response.data);

      setSuccess("API credentials generated successfully!");

      setShowCredentialForm(false);

      setSelectedOrgId("");

    } catch (error) {
      console.log(
        "Generate credentials error:",
        error.response?.data || error.message
      );

      setError(
        error.response?.data?.detail ||
        error.response?.data?.message ||
        "Unable to generate API credentials."
      );

    } finally {
      setGeneratingCredentials(false);
    }
  };

  const handleCreateWallet = async (e) => {
    e.preventDefault();

    if (!selectedWalletOrgId) {
      setError("Please select an organization.");
      return;
    }

    try {
      setCreatingWallet(true);
      setError("");
      setSuccess("");
      setWallet(null);

      const token = localStorage.getItem("access_token");

      const response = await axios.post(
        `http://127.0.0.1:8000/api/v1/admin/organizations/${selectedWalletOrgId}/wallet`,
        {
          currency: walletCurrency
        },
        {
          headers: {
            access_token: token
          }
        }
      );

      setWallet(response.data);
      setSuccess("Organization wallet created successfully!");
      setShowWalletForm(false);
      setSelectedWalletOrgId("");

    } catch (error) {
      setError(
        error.response?.data?.detail ||
        error.response?.data?.message ||
        "Unable to create wallet."
      );
    } finally {
      setCreatingWallet(false);
    }
  };


  const handleAddBalance = async (e) => {
    e.preventDefault();

    if (!selectedCreditOrgId) {
      setError("Please select an organization.");
      return;
    }

    try {
      setAddingBalance(true);
      setError("");
      setSuccess("");
      setCreditResult(null);

      const token = localStorage.getItem("access_token");

      const response = await axios.post(
        `http://127.0.0.1:8000/api/v1/admin/organizations/${selectedCreditOrgId}/wallet/credit`,
        {
          amount: Number(creditAmount),
          description: creditDescription
        },
        {
          headers: {
            access_token: token
          }
        }
      );

      setCreditResult(response.data);
      setSuccess("Wallet balance added successfully!");

      setShowCreditForm(false);
      setSelectedCreditOrgId("");
      setCreditAmount("");
      setCreditDescription("");

    } catch (error) {
      setError(
        error.response?.data?.detail ||
        error.response?.data?.message ||
        "Unable to add wallet balance."
      );
    } finally {
      setAddingBalance(false);
    }
  };


  const handleWalletStatus = async (e) => {
    e.preventDefault();

    try {
      setUpdatingWalletStatus(true);
      setError("");
      setSuccess("");

      const token = localStorage.getItem("access_token");

      await axios.patch(
        `http://127.0.0.1:8000/api/v1/admin/organizations/${selectedWalletStatusOrgId}/wallet/status`,
        {
          is_active: walletStatus === "true"
        },
        {
          headers: {
            access_token: token
          }
        }
      );

      setSuccess("Wallet status updated successfully!");
      setShowWalletStatusForm(false);
      setSelectedWalletStatusOrgId("");

    } catch (error) {
      setError(
        error.response?.data?.detail ||
        error.response?.data?.message ||
        "Unable to update wallet status."
      );
    } finally {
      setUpdatingWalletStatus(false);
    }
  };


  const handleOrganizationStatus = async (e) => {
    e.preventDefault();

    try {
      setUpdatingOrgStatus(true);
      setError("");
      setSuccess("");

      const token = localStorage.getItem("access_token");

      await axios.patch(
        `http://127.0.0.1:8000/api/v1/admin/organizations/${selectedOrgStatusId}/status`,
        {
          is_active: orgStatus === "true"
        },
        {
          headers: {
            access_token: token
          }
        }
      );

      setSuccess("Organization status updated successfully!");
      setShowOrgStatusForm(false);
      setSelectedOrgStatusId("");
      setRefresh((prev) => prev + 1);

    } catch (error) {
      setError(
        error.response?.data?.detail ||
        error.response?.data?.message ||
        "Unable to update organization status."
      );
    } finally {
      setUpdatingOrgStatus(false);
    }
  };


  const handleViewOrganizationDetails = async (e) => {
    e.preventDefault();

    try {
      setLoadingDetails(true);
      setError("");
      setSuccess("");
      setOrganizationDetails(null);

      const token = localStorage.getItem("access_token");

      const response = await axios.get(
        `http://127.0.0.1:8000/api/v1/admin/organizations/${selectedDetailsOrgId}`,
        {
          headers: {
            access_token: token
          }
        }
      );

      setOrganizationDetails(response.data.data);
      setShowDetailsForm(false);

    } catch (error) {
      setError(
        error.response?.data?.detail ||
        error.response?.data?.message ||
        "Unable to fetch organization details."
      );
    } finally {
      setLoadingDetails(false);
    }
  };

    // =====================================
  // 4. RENDER UI
  // =====================================

  return (
    <div className="organizations-content">

      {/* PAGE HEADING */}
      <div className="organizations-heading">

        <div>
          <h1>Organizations</h1>
          <p>Manage all registered organizations</p>
        </div>

        <div className="organization-actions">

          <button
            type="button"
            className="add-organization-btn"
            onClick={() => {
              setError("");
              setSuccess("");
              setShowCredentialForm(false);
              setShowForm(true);
            }}
          >
            + Add Organization
          </button>

          <button
            type="button"
            className="add-organization-btn"
            onClick={() => {
              setError("");
              setSuccess("");
              setCredentials(null);
              setShowForm(false);
              setShowCredentialForm(true);
            }}
          >
            <KeyRound size={16} />
            Generate API Credentials
          </button>

          <button
            type="button"
            className="add-organization-btn"
            onClick={() => {
              setError("");
              setSuccess("");
              setShowForm(false);
              setShowCredentialForm(false);
              setShowWalletForm(true);
              setWallet(null);
            }}
          > 
            <Wallet size={16} />
            Create Wallet
          </button>

          <button
            type="button"
            className="add-organization-btn"
            onClick={() => {
              setError("");
              setSuccess("");
              setShowForm(false);
              setShowCredentialForm(false);
              setShowWalletForm(false);
              setShowCreditForm(true);
              setCreditResult(null);
            }}
          >
            <HandCoins size={16} />
            Add Balance
          </button>


          <button
            type="button"
            className="add-organization-btn"
            onClick={() => {
              setError("");
              setSuccess("");
              setShowForm(false);
              setShowCredentialForm(false);
              setShowWalletForm(false);
              setShowCreditForm(false);
              setShowWalletStatusForm(true);
            }}
          >
            <Wallet size={16} />
            Wallet Status
          </button>

          <button
            type="button"
            className="add-organization-btn"
            onClick={() => {
              setError("");
              setSuccess("");
              setShowForm(false);
              setShowCredentialForm(false);
              setShowWalletForm(false);
              setShowCreditForm(false);
              setShowWalletStatusForm(false);
              setShowOrgStatusForm(true);
            }}
          >
            <Building2 size={16} />
            Organization Status
          </button>

          <button
            type="button"
            className="add-organization-btn"
            onClick={() => {
              setError("");
              setSuccess("");
              setShowForm(false);
              setShowCredentialForm(false);
              setShowWalletForm(false);
              setShowCreditForm(false);
              setShowWalletStatusForm(false);
              setShowOrgStatusForm(false);
              setOrganizationDetails(null);
              setShowDetailsForm(true);
            }}
          >
            <Building2 size={16} />
            View Organization Details
          </button>

        </div>
      </div>


      {/* SUCCESS MESSAGE */}
      {success && (
        <p className="success-message">
          {success}
        </p>
      )}


      {/* ERROR MESSAGE */}
      {error && (
        <p className="error-message">
          {error}
        </p>
      )}


      {/* =====================================
          CREATE ORGANIZATION FORM
      ===================================== */}

      {showForm && (
        <div className="organization-form-card">

          <h2>Create Organization</h2>

          <form onSubmit={handleCreateOrganization}>

            <input
              type="text"
              placeholder="Organization Name"
              value={formData.org_name}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  org_name: e.target.value
                })
              }
              minLength={2}
              maxLength={150}
              required
            />

            <input
              type="email"
              placeholder="Email Address"
              value={formData.email}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  email: e.target.value
                })
              }
              required
            />

            <input
              type="tel"
              placeholder="Phone Number (10 digits)"
              value={formData.phone}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  phone: e.target.value
                })
              }
              minLength={10}
              maxLength={10}
              required
            />

            <input
              type="password"
              placeholder="Password (minimum 8 characters)"
              value={formData.password}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  password: e.target.value
                })
              }
              minLength={8}
              required
            />

            <button
              type="submit"
              disabled={creating}
            >
              {creating
                ? "Creating Organization..."
                : "Create Organization"}
            </button>

            <button
              type="button"
              onClick={() => setShowForm(false)}
              disabled={creating}
            >
              Cancel
            </button>

          </form>
        </div>
      )}


      {/* =====================================
          GENERATE API CREDENTIALS FORM
      ===================================== */}

      {showCredentialForm && (
        <div className="organization-form-card">

          <h2>Generate API Credentials</h2>

          <form onSubmit={handleGenerateCredentials}>

            <label htmlFor="organization-select">
              Select Organization
            </label>

            <select
              id="organization-select"
              value={selectedOrgId}
              onChange={(e) => setSelectedOrgId(e.target.value)}
              required
            >
              <option value="">
                Select an organization
              </option>

              {organizations.map((org) => (
                <option
                  key={org.org_id}
                  value={org.org_id}
                >
                  {org.org_name} ({org.org_id})
                </option>
              ))}
            </select>

            <button
              type="submit"
              disabled={
                generatingCredentials ||
                !selectedOrgId
              }
            >
              {generatingCredentials
                ? "Generating Credentials..."
                : "Generate Credentials"}
            </button>

            <button
              type="button"
              onClick={() => {
                setShowCredentialForm(false);
                setSelectedOrgId("");
              }}
              disabled={generatingCredentials}
            >
              Cancel
            </button>

          </form>
        </div>
      )}

      {showWalletForm && (
        <div className="organization-form-card">
          <h2>Create Organization Wallet</h2>

          <form onSubmit={handleCreateWallet}>
            <label htmlFor="wallet-organization">
              Select Organization
            </label>

            <select
              id="wallet-organization"
              value={selectedWalletOrgId}
              onChange={(e) =>
                setSelectedWalletOrgId(e.target.value)
              }
              required
            >
              <option value="">Select an organization</option>

              {organizations.map((org) => (
                <option key={org.org_id} value={org.org_id}>
                  {org.org_name} ({org.org_id})
                </option>
              ))}
            </select>

            <label htmlFor="wallet-currency">
              Currency
            </label>

            <select
              id="wallet-currency"
              value={walletCurrency}
              onChange={(e) => setWalletCurrency(e.target.value)}
            >
              <option value="INR">INR</option>
            </select>

            <button type="submit" disabled={creatingWallet}>
              {creatingWallet ? "Creating Wallet..." : "Create Wallet"}
            </button>

            <button
              type="button"
              onClick={() => setShowWalletForm(false)}
              disabled={creatingWallet}
            >
              Cancel
            </button>
          </form>
        </div>
      )}

      {showCreditForm && (
          <div className="organization-form-card">
            <h2>Add Balance to Organization Wallet</h2>

            <form onSubmit={handleAddBalance}>

              <label>Select Organization</label>

              <select
                value={selectedCreditOrgId}
                onChange={(e) =>
                  setSelectedCreditOrgId(e.target.value)
                }
                required
              >
                <option value="">Select an organization</option>

                {organizations.map((org) => (
                  <option key={org.org_id} value={org.org_id}>
                    {org.org_name}
                  </option>
                ))}
              </select>

              <label>Amount (INR)</label>

              <input
                type="number"
                placeholder="Enter amount"
                value={creditAmount}
                onChange={(e) => setCreditAmount(e.target.value)}
                min="0.01"
                step="0.01"
                required
              />

              <label>Description</label>

              <input
                type="text"
                placeholder="Enter transaction description"
                value={creditDescription}
                onChange={(e) =>
                  setCreditDescription(e.target.value)
                }
                minLength={3}
                maxLength={255}
                required
              />

              <button type="submit" disabled={addingBalance}>
                {addingBalance ? "Adding Balance..." : "Add Balance"}
              </button>

              <button
                type="button"
                onClick={() => setShowCreditForm(false)}
                disabled={addingBalance}
              >
                Cancel
              </button>

            </form>
          </div>
        )}

        {showWalletStatusForm && (
          <div className="organization-form-card">

            <h2>Update Wallet Status</h2>

            <form onSubmit={handleWalletStatus}>

              <label>Select Organization</label>

              <select
                value={selectedWalletStatusOrgId}
                onChange={(e) =>
                  setSelectedWalletStatusOrgId(e.target.value)
                }
                required
              >
                <option value="">Select an organization</option>

                {organizations.map((org) => (
                  <option key={org.org_id} value={org.org_id}>
                    {org.org_name}
                  </option>
                ))}
              </select>

              <label>Wallet Status</label>

              <select
                value={walletStatus}
                onChange={(e) => setWalletStatus(e.target.value)}
              >
                <option value="true">Activate Wallet</option>
                <option value="false">Deactivate Wallet</option>
              </select>

              <button
                type="submit"
                disabled={updatingWalletStatus || !selectedWalletStatusOrgId}
              >
                {updatingWalletStatus
                  ? "Updating..."
                  : "Update Wallet Status"}
              </button>

              <button
                type="button"
                onClick={() => setShowWalletStatusForm(false)}
                disabled={updatingWalletStatus}
              >
                Cancel
              </button>

            </form>
          </div>
        )}

        {showOrgStatusForm && (
          <div className="organization-form-card">
            <h2>Update Organization Status</h2>

            <form onSubmit={handleOrganizationStatus}>

              <label>Select Organization</label>

              <select
                value={selectedOrgStatusId}
                onChange={(e) => setSelectedOrgStatusId(e.target.value)}
                required
              >
                <option value="">Select an organization</option>

                {organizations.map((org) => (
                  <option key={org.org_id} value={org.org_id}>
                    {org.org_name}
                  </option>
                ))}
              </select>

              <label>Organization Status</label>

              <select
                value={orgStatus}
                onChange={(e) => setOrgStatus(e.target.value)}
              >
                <option value="true">Activate Organization</option>
                <option value="false">Deactivate Organization</option>
              </select>

              <button
                type="submit"
                disabled={updatingOrgStatus || !selectedOrgStatusId}
              >
                {updatingOrgStatus ? "Updating..." : "Update Organization Status"}
              </button>

              <button
                type="button"
                onClick={() => setShowOrgStatusForm(false)}
                disabled={updatingOrgStatus}
              >
                Cancel
              </button>

            </form>
          </div>
        )}


        {showDetailsForm && (
          <div className="organization-form-card">
            <h2>View Organization Details</h2>

            <form onSubmit={handleViewOrganizationDetails}>
              <label>Select Organization</label>

              <select
                value={selectedDetailsOrgId}
                onChange={(e) => setSelectedDetailsOrgId(e.target.value)}
                required
              >
                <option value="">Select an organization</option>

                {organizations.map((org) => (
                  <option key={org.org_id} value={org.org_id}>
                    {org.org_name}
                  </option>
                ))}
              </select>

              <button type="submit" disabled={loadingDetails}>
                {loadingDetails ? "Fetching Details..." : "View Details"}
              </button>

              <button
                type="button"
                onClick={() => setShowDetailsForm(false)}
                disabled={loadingDetails}
              >
                Cancel
              </button>
            </form>
          </div>
        )}


      {/* SEARCH */}
      <div className="organizations-toolbar">

        <div className="organization-search">

          <Search size={18} />

          <input
            type="text"
            placeholder="Search by organization name or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />

        </div>

      </div>


      {/* =====================================
          ORGANIZATIONS TABLE
      ===================================== */}

      <div className="organizations-table-container">

        <table className="organizations-table">

          <thead>
            <tr>
              <th>Organization</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Status</th>
              <th>Created At</th>
            </tr>
          </thead>

          <tbody>

            {loading ? (

              <tr>
                <td colSpan="5">
                  Loading organizations...
                </td>
              </tr>

            ) : organizations.length > 0 ? (

              organizations.map((org) => (

                <tr key={org.org_id}>

                  <td>
                    <div className="organization-name">
                      <Building2 size={18} />
                      {org.org_name}
                    </div>
                  </td>

                  <td>{org.email}</td>

                  <td>{org.phone}</td>

                  <td>
                    <span
                      className={`organization-status ${
                        org.is_active ? "active" : "inactive"
                      }`}
                    >
                      {org.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>

                  <td>
                    {org.created_at
                      ? new Date(
                          org.created_at
                        ).toLocaleDateString("en-IN")
                      : "-"}
                  </td>

                </tr>

              ))

            ) : (

              <tr>
                <td colSpan="5">
                  No organizations found.
                </td>
              </tr>

            )}

          </tbody>

        </table>

      </div>


      {/* =====================================
          DISPLAY GENERATED CREDENTIALS
      ===================================== */}

      {credentials && (
        <div className="credentials-card">

          <h3>Organization API Credentials</h3>

          <p>
            <strong>Organization ID:</strong>
            {" "}{credentials.id}
          </p>

          <p>
            <strong>API Key:</strong>
            {" "}{credentials.api_key}
          </p>

          <p>
            <strong>API Secret:</strong>
            {" "}{credentials.api_secret}
          </p>

          <p>
            Save these credentials securely.
            The API secret is shown only once.
          </p>

        </div>
      )}


      {wallet && (
        <div className="credentials-card">
          <h3>Wallet Created Successfully</h3>

          <p>
            <strong>Wallet ID:</strong> {wallet.wallet_id}
          </p>

          <p>
            <strong>Currency:</strong> {wallet.currency}
          </p>

          <p>
            <strong>Balance:</strong> {wallet.balance}
          </p>

          <p>
            <strong>Status:</strong> {wallet.is_active ? "Active" : "Inactive"}
          </p>
        </div>
      )}


      {organizationDetails && (
        <div className="credentials-card">
          <h3>Organization Details</h3>

          <p>
            <strong>Organization ID:</strong>{" "}
            {organizationDetails.org_id}
          </p>

          <p>
            <strong>Name:</strong>{" "}
            {organizationDetails.org_name}
          </p>

          <p>
            <strong>Email:</strong>{" "}
            {organizationDetails.email}
          </p>

          <p>
            <strong>Phone:</strong>{" "}
            {organizationDetails.phone}
          </p>

          <p>
            <strong>Status:</strong>{" "}
            {organizationDetails.is_active ? "Active" : "Inactive"}
          </p>

          {organizationDetails.wallet && (
            <>
              <h3>Wallet Details</h3>

              <p>
                <strong>Currency:</strong>{" "}
                {organizationDetails.wallet.currency}
              </p>

              <p>
                <strong>Balance:</strong>{" "}
                {organizationDetails.wallet.balance}
              </p>

              <p>
                <strong>Status:</strong>{" "}
                {organizationDetails.wallet.is_active
                  ? "Active"
                  : "Inactive"}
              </p>
            </>
          )}
        </div>
      )}

    </div>
  );
}

export default Organizations;
