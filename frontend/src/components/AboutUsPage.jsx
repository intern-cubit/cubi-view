import React from 'react';

const AboutUsPage = () => {
  const aboutText = (
    <>
      <p className="mb-4">We are a stealth-mode company building fully customized hardware and software solutions.</p>
      <p className="mb-4">No templated products, no fluff — just exact quotations, high-quality R&D, and on-time delivery.</p>
      <p className="mb-4">Every project is case-specific, crafted by a dedicated team including experts from Germany & China.</p>
      <p className="mb-4">We don’t just advertise — we deliver.</p>
      <p className="mb-4">Want us to customize a product for you? Or build something entirely new?</p>
      <p className="mb-4">Connect with us now!</p>
      <p className="mt-6 text-xl font-bold">
        www.cubitdynamics.com | info@cubitdynamics.com | +91 86185 09818
      </p>
    </>
  );

  return (
    <div className="container mx-auto my-8">
      <h3 className="text-4xl font-extrabold mb-6 text-cubit-gold">About CuBIT Dynamics</h3>

      <div className="bg-white p-10 shadow-xl rounded-lg text-center">
        {/* Uncomment and adjust if you have a CuBIT logo */}
        {/* <img src={logo} alt="CuBIT Dynamics Logo" className="mb-6 mx-auto w-48" /> */}

        <div className="text-left text-lg leading-relaxed text-cubit-brown max-w-2xl mx-auto">
          {aboutText}
        </div>
      </div>
    </div>
  );
};

export default AboutUsPage;